CREATE OR REPLACE FUNCTION xllm_bulk_upsert_hash_ids(records JSONB)
RETURNS void AS $$
DECLARE
    record JSONB;
    record_text TEXT;
	v_table_name TEXT := 'xllm_hash_id';
BEGIN
    -- Loop through JSONB array and process each record
    FOR record IN SELECT * FROM jsonb_array_elements(records) LOOP
        BEGIN
            -- Convert JSONB record to text for logging
            record_text := record::TEXT;

            -- Insert or update the record
            INSERT INTO xllm_hash_id (key, hashes)
            VALUES (record->>'key', (record->>'hashes')::JSONB)
            ON CONFLICT (key) DO UPDATE
            SET hashes = EXCLUDED.hashes;

        EXCEPTION WHEN others THEN
            -- Log failed record into error log table
            INSERT INTO xllm_load_run_error_log (table_name, error_message, record_text)
            VALUES (v_table_name, SQLERRM, record_text);
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;