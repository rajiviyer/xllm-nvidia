CREATE OR REPLACE FUNCTION process_query(query_params JSONB )
RETURNS TABLE (
    id TEXT,
    content JSONB,
    size INT,
    agents TEXT,
    rank INT
) AS $$
DECLARE
	v_query_text TEXT[] := (SELECT array_agg(value) FROM jsonb_array_elements_text(query_params->'query_text'));
	v_stemmed_text TEXT[]:= (SELECT array_agg(value) FROM jsonb_array_elements_text(query_params->'stemmed_text'));
	v_use_stem BOOL := query_params->> 'use_stem';
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
	RAISE NOTICE 'Beta %', v_beta;

	WITH query_tokens AS 
	(
		SELECT unnest(v_query_text) AS query_token
	),
	stemmed_tokens AS 
	(
		SELECT unnest(v_stemmed_text) AS stemmed_token where true = v_use_stem
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

--	COMMIT;

	FOR v_record in (select token, frequency from temp_dictionary) LOOP
		v_record_text := v_record::TEXT;
		RAISE NOTICE 'dictionary record: %', v_record_text;
	END LOOP; 

	DROP TABLE IF EXISTS temp_embeddings;

	CREATE TEMP TABLE temp_embeddings(
		token TEXT,
		embedding TEXT,
		pmi FLOAT
	) ON COMMIT PRESERVE ROWS;

	INSERT INTO temp_embeddings(token, embedding, pmi)
	SELECT 
	    xe."key"::TEXT as token, 
	    j.key::TEXT AS embedding, 
	    j.value::FLOAT as pmi
	FROM xllm_embeddings xe , 
	    jsonb_each(embeddings) j
	    where xe."key" in (select token from temp_dictionary);

--	COMMIT;

--	FOR v_record in (select token, embedding, pmi from temp_embeddings) LOOP
--		v_record_text := v_record::TEXT;
--		RAISE NOTICE 'embedding record: %', v_record_text;
--	END LOOP; 

	RETURN QUERY
		with chunk_data as
		(
		select xhi."key" as token,
			j.key as chunk_id,
			j.value::INT as chunk_freq,
			d.frequency as token_freq
			from xllm_hash_id xhi,
			jsonb_each(hashes) j,
			temp_dictionary d
			where xhi."key" = d.token
		),
		chunk_scores as
		(
			select chunk_id, sum(1/power(token_freq,1)) as weight1, count(*) as weight2
			from chunk_data
			group by chunk_id
		),
		chunk_ranks as 
		(
			select chunk_id, weight1, weight2, 
			dense_rank() over (order by weight1 desc) as rnk1, 
			dense_rank() over (order by weight2 desc) as rnk2
			from chunk_scores
		) ,
		chunk_weighted_rank as
		(
			select chunk_id, 2*rnk1 + rnk2 as weighted_rank_score, dense_rank() over(order by (2*rnk1 + rnk2)) as final_rank
			from chunk_ranks
		)
		select cwr.chunk_id as id, xcd.content::JSONB, xcd.size::INT, xcd.agents::TEXT, cwr.weighted_rank_score::INT as rankx 
		from chunk_weighted_rank cwr, xllm_chunk_details xcd
		where cwr.chunk_id = xcd.chunk_id
		order by cwr.final_rank;
END;
$$ LANGUAGE plpgsql;