CREATE OR REPLACE FUNCTION public.xllm_bulk_upsert_chunks(records jsonb)
RETURNS void AS $$
DECLARE
    record JSONB;
    record_text TEXT;
	v_table_name TEXT := 'xllm_chunk_details';
BEGIN
    -- Loop through JSONB array and process each record
    FOR record IN SELECT * FROM jsonb_array_elements(records) LOOP
        BEGIN
            -- Convert JSONB record to text for logging
            record_text := record::TEXT;

            -- Insert or update the record
            INSERT INTO xllm_chunk_details (chunk_id, size)
            VALUES (record->>'chunk_id', (record->>'size')::INTEGER)
            ON CONFLICT (chunk_id) DO UPDATE
            SET size = EXCLUDED.size;

        EXCEPTION WHEN others THEN
            -- Log failed record into error log table
            INSERT INTO xllm_load_run_error_log (table_name, error_message, record_text)
            VALUES (v_table_name, SQLERRM, record_text);
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;