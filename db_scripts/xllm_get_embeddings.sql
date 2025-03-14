CREATE OR REPLACE FUNCTION xllm_get_embeddings(query_params JSONB )
RETURNS TABLE (
	word TEXT,
	embedding TEXT,
	pmi FLOAT
) AS $$
DECLARE
	v_query_text TEXT[] := (SELECT array_agg(value) FROM jsonb_array_elements_text(query_params->'query_text'));
	v_stemmed_text TEXT[]:= (SELECT array_agg(value) FROM jsonb_array_elements_text(query_params->'stemmed_text'));
	v_use_stem BOOLEAN := query_params->> 'use_stem';
	v_distill BOOLEAN := query_params->> 'distill';
	v_max_token_count INT := query_params->>'max_token_count';
	v_beta FLOAT := query_params->> 'beta';
	v_final_tokens TEXT[];
	v_combined_tokens TEXT[];
	binary_num INT;
    token_combination TEXT;
    n INT;
	v_expanded_tokens TEXT[];
	v_record RECORD;
	v_record_text TEXT;
	v_record_count INT;
	v_chunk_rank_result JSONB[];
BEGIN	

    RAISE NOTICE 'Query Text %', v_query_text;
    RAISE NOTICE 'Stemmed Text %', v_stemmed_text;
    RAISE NOTICE 'Use Stem? %', v_use_stem;
    RAISE NOTICE 'Distill? %', v_distill;
	RAISE NOTICE 'Max Token Count %', v_max_token_count;
    RAISE NOTICE 'Beta %', v_beta;


	-- Step 1: Extract Final Tokens
	WITH
	query_tokens AS 
	(
		SELECT unnest(v_query_text) AS query_token
	),
 	stemmed_tokens AS 
	(
		SELECT unnest(
					CASE 
						WHEN v_use_stem THEN v_stemmed_text
						ELSE ARRAY[]::TEXT[]
					END
			) AS stemmed_token
	),
	unstemmed_tokens AS
	(
		SELECT regexp_split_to_table(keywords, E', ') as unstemmed_token
		from xllm_hash_unstem where stem in (select stemmed_token from stemmed_tokens)
	),
	final_tokens AS
	(
		select final_token from
		(
			SELECT query_token as final_token from query_tokens where query_token 
			in (select token from xllm_dictionary)
			UNION
			SELECT unstemmed_token as final_token from unstemmed_tokens
		)
		order by final_token
	)
	SELECT array_agg(final_token) INTO v_final_tokens FROM final_tokens;
	
	RAISE NOTICE 'Final Tokens: %', v_final_tokens;


	n := array_length(v_final_tokens, 1);

	-- Step 2: Generate N-Gram Combinations (Bitwise Logic)
    -- Generate all possible binary combinations (1 to 2^N - 1)
    FOR binary_num IN 1 .. (POWER(2, n) - 1) LOOP
        token_combination := '';  -- Reset for each iteration
        
        --Iterate over each bit position (word index)
        FOR i IN 1 .. n LOOP
             --Check if the i-th bit is set (binary_num AND (2^(i-1)))
            IF (binary_num & POWER(2, i-1)::INT) > 0 THEN
                 --Concatenate words using ~ separator
                IF token_combination IS NULL or token_combination = '' THEN
                    token_combination := v_final_tokens[i];
				ELSE
					token_combination := token_combination || '~' || v_final_tokens[i];
                END IF;
            END IF;
        END LOOP;
        
         --Store generated n-gram combination
        v_combined_tokens := array_append(v_combined_tokens, token_combination); 
    END LOOP;

	RAISE NOTICE 'Combined Tokens: %', v_combined_tokens; 
	
	-- Step 3: Create Temporary Dictionary Table
	DROP TABLE IF EXISTS temp_dictionary;
	CREATE TEMP TABLE temp_dictionary (
		token TEXT PRIMARY KEY,
		frequency FLOAT
	) ON COMMIT PRESERVE ROWS;

	INSERT INTO temp_dictionary(token, frequency)
	WITH combined_tokens AS 
	(
		SELECT unnest(v_combined_tokens) AS combined_token
	),
	sorted_ngram_tokens AS
	(
		SELECT regexp_split_to_table(ngrams, E', ') AS ngram_token
		FROM xllm_sorted_ngrams
		WHERE key IN (SELECT combined_token FROM combined_tokens)
	)
	SELECT token, frequency FROM xllm_dictionary WHERE token IN (SELECT ngram_token FROM sorted_ngram_tokens);

	-- Step 4: Insert multi-tokens in temp_dictionary
	INSERT INTO temp_dictionary(token, frequency)
	with combined_tokens as 
	(
		select unnest(v_combined_tokens) AS combined_token
	),
	multi_tokens as
	(
		select combined_token as multi_token from combined_tokens where combined_token like '%~%' and 
		combined_token not in (select token from temp_dictionary)
	)
	select token, frequency from xllm_dictionary where token in (select multi_token from multi_tokens);

	-- Step 5: Apply `distill` Logic If `v_distill = TRUE`

    IF v_distill THEN
        -- Remove tokens exceeding `maxTokenCount`
        DELETE FROM temp_dictionary WHERE frequency > v_max_token_count;

        -- Remove redundant n-grams
        DELETE FROM temp_dictionary t1
	    WHERE EXISTS (
	        SELECT 1 FROM temp_dict t2
	        WHERE t1.token <> t2.token
	        AND (
	            (POSITION(t1.token IN t2.token) > 0 and t1.frequency = t2.frequency)
	            or (t1.token IN (SELECT UNNEST(STRING_TO_ARRAY(t2.token, '~'))))
	        )
	    );
    END IF;

    -- Debugging Output for Dictionary Cleanup
    SELECT COUNT(*) INTO v_record_count FROM temp_dictionary;
    RAISE NOTICE 'Final Dictionary Record Count: %', v_record_count;

	return QUERY
		SELECT 
		    xe."key"::TEXT as word, 
		    j.key::TEXT AS embedding, 
		    j.value::FLOAT as pmi
		FROM xllm_embeddings xe , 
		    jsonb_each(embeddings) j
		    where xe."key" in (select td.token from temp_dictionary td)
		order by 3 desc;
	
END;
$$ LANGUAGE plpgsql;	