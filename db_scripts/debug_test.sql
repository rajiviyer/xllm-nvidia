with 
cleaned_tokens as
(
	SELECT word as cleaned_token
	FROM unnest(string_to_array(regexp_replace(lower('What are the Data Center Highlights?'), '[[:punct:]]', ' ', 'g'), ' ')) AS word
	WHERE word IS NOT NULL AND word <> ''
),
stemmed_tokens as
(
	select to_tsvector('english', cleaned_token)::text as stemmed_token
	from cleaned_tokens
)
select trim(split_part(stemmed_token,':',1),'''') from stemmed_tokens where stemmed_token <> '';


SELECT ts_headline('english', 'what are the data center highlights');

SELECT to_tsvector('english', 'running jumps highlighted data center');


SELECT *
FROM unnest(string_to_array('what are the data center highlights', ' ')) AS word,
(to_tsvector('english', word)::jsonb) AS lexeme;


SELECT array_agg(DISTINCT jsonb_object_keys(to_tsvector('english', word)::jsonb))
FROM unnest(string_to_array('what are the data center highlights', ' ')) AS word;



select regexp_split_to_table(keywords, E', ') as unstemmed_token from xllm_hash_unstem xhu where stem = 'center';

select * from temp_dictionary;

select * from xllm_embeddings where key = 'whats';

SELECT 
    xe."key" as token, 
    j.key AS embedding, 
    j.value::FLOAT AS embedding_value 
FROM xllm_embeddings xe , 
    jsonb_each(embeddings) j
    where xe."key" = 'whats';

SELECT ts_headline('english', 'what');

drop table temp_dict;
create table temp_dict as
select token, frequency from xllm_dictionary xd where token in 
('data~centers','center','highlights~data','centers','highlights','highlights~data~center','data~center','data','whats');

select token, frequency from temp_dict
except
select token, frequency from
temp_dict t1
    WHERE EXISTS (
        SELECT 1 FROM temp_dict t2
        WHERE t1.token <> t2.token
        AND (
            (POSITION(t1.token IN t2.token) > 0 and t1.frequency = t2.frequency)
            or (t1.token IN (SELECT UNNEST(STRING_TO_ARRAY(t2.token, '~'))))
        )
    );

select * from temp_dict;

select position('highlights~data~center' in 'data~center');
select position('data~center' in 'highlights~data~center');

SELECT * FROM xllm_get_docs(
    '{"query_text": ["what", "are", "the", "data", "center", "highlights"],
      "stemmed_text": ["what", "are", "the", "data", "center", "highlight"],
	  "distill": true,
	  "max_token_count": 500,
      "use_stem": false,
      "beta": 1.0}'::jsonb
);


SELECT * FROM xllm_get_embeddings(
    '{"query_text": ["what", "are", "the", "data", "center", "highlights"],
      "stemmed_text": ["what", "are", "the", "data", "center", "highlight"],
	  "distill": true,
	  "max_token_count": 500,
      "use_stem": false,
      "beta": 1.0}'::jsonb
);

with chunk_data as
(
select xhi."key" as token,
	j.key as chunk_id,
	j.value::INT as chunk_freq,
	d.frequency as token_freq
	from xllm_hash_id xhi,
	jsonb_each(hashes) j,
	(select * from xllm_dictionary xd 
		where xd.token in 
		('data~centers','center','highlights~data','centers','highlights','highlights~data~center',
		'data~center','data','whats')
	) d
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
select cwr.chunk_id as id, xcd.content, xcd.size, xcd.agents, cwr.weighted_rank_score as rankx 
from chunk_weighted_rank cwr, xllm_chunk_details xcd
where cwr.chunk_id = xcd.chunk_id
order by cwr.final_rank;





select chunk_id, content, size, agents from xllm_chunk_details;

select * from xllm_hash_id xhi ;


select xhi."key" as token,
	j.key as chunk_id,
	j.value::INT as chunk_freq,
	d.frequency as token_freq,
	1/power(d.frequency,1) weight1
	from xllm_hash_id xhi,
	jsonb_each(hashes) j,
	(select * from xllm_dictionary xd 
		where xd.token in 
		('data~centers','center','highlights~data','centers','highlights','highlights~data~center',
		'data~center','data','whats')
	) d
	where xhi."key" = d.token
	and j.key = 'B50X2';

select count(*) from embeddings e where parent = 'growth~data';

select count(*) from xllm_embeddings;


WITH query_tokens AS 
(
	SELECT unnest(ARRAY['what', 'are', 'data', 'center', 'highlights']) AS query_token
),
stemmed_tokens AS 
(
	SELECT unnest(
				CASE 
					WHEN false THEN ARRAY['what', 'are', 'data', 'center', 'highlight']
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
SELECT array_agg(final_token) FROM final_tokens;
