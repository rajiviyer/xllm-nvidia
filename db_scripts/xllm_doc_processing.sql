DO $$ 
<<first_block>>
DECLARE
	query_text TEXT[] := ARRAY[
		'what', 'are', 'the', 'main', 'data', 'center', 'highlights'
	];

	stemmed_words TEXT[] := ARRAY[
		'what', 'are', 'the', 'main', 'data', 'center', 'highlight'
	];

	v_final_tokens TEXT[];
	v_combined_tokens TEXT[];
	binary_num INT;
    token_combination TEXT;
    n INT;
	v_expanded_tokens TEXT[];
	v_dictionary_record RECORD;
	v_record_text TEXT;
	v_record_count INT;
BEGIN

	WITH query_tokens AS 
	(
		SELECT unnest(query_text) AS query_token
	),
	stemmed_tokens AS 
	(
		SELECT unnest(stemmed_words) AS stemmed_token
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
	
	DROP TABLE IF EXISTS temp_dictionary;

	CREATE TEMP TABLE temp_dictionary (
		token TEXT PRIMARY KEY,
		frequency FLOAT
	) ON COMMIT PRESERVE ROWS;


	insert into temp_dictionary(token, frequency)
	with combined_tokens as 
	(
		select unnest(v_combined_tokens) AS combined_token
	),
	sorted_ngram_tokens as
	(
		select regexp_split_to_table(ngrams, E', ') as ngram_token
		from xllm_sorted_ngrams
		where key in (select combined_token from combined_tokens)
	)
	select token, frequency from xllm_dictionary where token in (select ngram_token from sorted_ngram_tokens);

	select count(*) into v_record_count from temp_dictionary;
	
	RAISE NOTICE 'record_count %', v_record_count;

	insert into temp_dictionary(token, frequency)
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


	select count(*) into v_record_count from temp_dictionary;
	RAISE NOTICE 'record_count %', v_record_count;

	COMMIT;

	FOR v_dictionary_record in (select token, frequency from temp_dictionary) LOOP
		v_record_text := v_dictionary_record::TEXT;
		RAISE NOTICE 'record: %', v_record_text;
	END LOOP; 

	
	


END first_block $$;