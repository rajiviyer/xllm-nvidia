from .utils.types import frontendParamsType
from typing import Optional, List
from .utils.params import (get_bin, ignore, sample_queries, 
                     sectionLabels, backendTables)

from .utils import functions as exllm
from .llm_processing import parse_docs

from nltk.stem import PorterStemmer
from collections import defaultdict
stemmer = PorterStemmer()

#--- Functions used to score results ---

def rank(hash):
    # sort hash, then replace values with their rank    

    hash = dict(sorted(hash.items(), key=lambda item: item[1], reverse=True))
    rank = 0
    old_value = 999999999999

    for key in hash:
        value = hash[key]
        if value < old_value:
            rank += 1
        hash[key] = rank
        old_value = value
    return(hash)


def rank_ID(ID_score): 
    # attach weighted relevancy rank to text entity ID, with respect to prompt

    ID_score0 = {}
    ID_score1 = {}
    ID_score2 = {}
    ID_score3 = {}

    for ID in ID_score:
        score = ID_score[ID]    
        ID_score0[ID] = score[0]
        ID_score1[ID] = score[1]
        ID_score2[ID] = score[2]
        ID_score3[ID] = score[3]

    ID_score0 = rank(ID_score0)
    ID_score1 = rank(ID_score1)
    ID_score2 = rank(ID_score2)
    ID_score3 = rank(ID_score3)

    ID_score_ranked = {}
    for ID in ID_score:
        weighted_rank = 2*ID_score0[ID] + ID_score1[ID] + ID_score2[ID] + ID_score3[ID]
        ID_score_ranked[ID] = weighted_rank
    ID_score_ranked = dict(sorted(ID_score_ranked.items(), key=lambda item: item[1]))
    return(ID_score_ranked)

def get_docs(form_params: frontendParamsType) -> dict[List[dict], List[dict]]:
    """
    Get docs

    Args:
        form_params (frontendParamsType): User Input Data from Frontend  

    Returns:
        List[dict]: Dictionary of List of Embeddings & Docs
    """
    print("form_params", form_params)
    use_stem = form_params['useStem']
    beta = form_params['beta']
    # hash_pairs = backendTables['hash_pairs']
    dictionary = backendTables['dictionary']
    ID_to_agents = backendTables['ID_to_agents']
    # ctokens = backendTables['ctokens']
    embeddings = backendTables["embeddings"]
    sorted_ngrams = backendTables["sorted_ngrams"]
    ID_to_content = backendTables['ID_to_content']
    hash_unstem = backendTables['hash_unstem']
    ID_index = backendTables['ID_to_index']
    ID_size  = backendTables['ID_size']    
    # KW_map = backendTables["KW_map"]
        
    query = form_params['queryText']
    query = query.split(' ')
    
    new_query = []
    neg_query = []  # keywords to exclude
    altTokens = ()    
    
    ### New Code
    new_query = []
    for k in range(len(query)):
        token = query[k].lower()
        print(f"Token: {token}")
        if token and token[0] == '!':
            token = token[1:len(token)]
            neg_query.append(token) 
            
        if use_stem:
            tstem = stemmer.stem(token)
            if tstem in hash_unstem:  
                tlist = hash_unstem[tstem] 
                for altToken in tlist:
                    if token != altToken and altToken not in altTokens :
                        altTokens = (*altTokens, altToken)                    
        if token in dictionary:
            new_query.append(token)
            
    q_altTokens = ()
    for altToken in altTokens:
        if altToken not in new_query:
            new_query.append(altToken)
            q_altTokens = (*q_altTokens, altTokens)   
                        
    query = new_query.copy()    
    query.sort()
    print("Cleaned:", query)
    print("------------------")
    print("Alttokens", altTokens)
        
    q_embeddings = {} 
    q_dictionary = {} 
    
    # Logic for retrieving docs
    for k in range(1, 2**len(query)): 

        binary = get_bin(k, len(query))
        sorted_word = ""
        for k in range(0, len(binary)):
            if binary[k] == '1':
                if sorted_word == "":
                    sorted_word = query[k]
                else:
                    sorted_word += "~" + query[k]

        if sorted_word in sorted_ngrams:
            ngrams = sorted_ngrams[sorted_word]
            for word in ngrams:
                if word in dictionary:
                    q_dictionary[word] = dictionary[word]
                    embedding = exllm.get_value(word, embeddings)
                    exllm.add_embedding(q_embeddings, word, embedding)
    
    print("qembeddings length", len(q_embeddings))
    print("q_dictionary length", len(q_dictionary))                       

    # deal with prompt multitokens, if there are any  [need to add multitoken stemming]
    for word in query:
        if '~' in word and word in dictionary and word not in q_dictionary:
            q_dictionary[word] = dictionary[word]
            embedding = exllm.get_value(word, embeddings)
            exllm.add_embedding(q_embeddings, word, embedding)
            
    print("qembeddings length", len(q_embeddings))
    print("q_dictionary length", len(q_dictionary))            
            

    # --- Scoring and selecting what to show in prompt results ---                
    if form_params['distill']:
        # gow is this working with negative keywords?
        exllm.distill_frontendTables(q_dictionary,q_embeddings,form_params) 
        
    hash_ID = backendTables['hash_ID']
    ID_hash = {} # local, transposed of hash_ID; key = ID; value = multitoken list    

    for word in q_dictionary:
        for ID in hash_ID[word]:
            local_hash = hash_ID[word]
            if word not in neg_query: 
                exllm.update_nestedHash(ID_hash, ID, word, local_hash[ID]) 
        gword = "__" + word  # graph multitoken 
        if gword in hash_ID and word not in neg_query:
            for ID in hash_ID[gword]:
                exllm.update_nestedHash(ID_hash, ID, gword, 1)     
    print("ID_hash length", len(ID_hash))        
    
    ID_score = {}
    for ID in ID_hash:
        # score[0] is inverse weighted count
        # score[1] is raw number of tokens found
        score  = [0, 0]  # based on tokens present in the entire text entity
        gscore = [0, 0]  # based on tokens present in graph (context elements)
        for token in ID_hash[ID]:
            if  token in dictionary:
                score[0] += 1/(q_dictionary[token]**beta)
                score[1] += 1
            else:
                # token must start with "__" (it's a graph token)
                token = token[2:len(token)]
                gscore[0] += 1/(q_dictionary[token]**beta)
                gscore[1] += 1
        ID_score[ID] = [score[0], score[1], gscore[0], gscore[1]]
        
    ID_score_ranked = rank_ID(ID_score) 
    nresults = form_params['nresults']
    print("ID_score length", len(ID_score))
    
    print("Most relevant chunks with multitokens, doc_ID, pn, rank, size:\n")
    
    n_ID = 0
    print("\n          ID wRank   size PDF   pn ID_Tokens")
    for ID in ID_score_ranked:
        if n_ID < nresults:  
            # content of text entity ID not shown, stored in ID_to_content[ID]
            # add tags
            mindex = ID_index[ID] # multi-index
            doc_ID = mindex[0]    # PDF number
            pn = mindex[1]        # page number within PDF
            rankx = ID_score_ranked[ID]  # need to also create ID_score[ID] (absolute score)
            size = ID_size[ID]
            print("    %8s   %3d %6d %3d %4d %s" 
                    %(ID, rankx, size, doc_ID, pn, ID_hash[ID]))     
        n_ID += 1
        
    print("Most relevant chunks with agents:\n")
    print("\n          ID     ID_agents")
    n_ID = 0            
    for ID in ID_score_ranked:
        if n_ID < nresults:  
            agents = exllm.get_value(ID, ID_to_agents)
            if len(agents) > 0:
                print("    %8s     %s" %(ID, agents))     
        n_ID += 1    
    
    print("\nToken count (via dictionary):\n")
    for key in q_dictionary:
        print("    %4d     %s" %(q_dictionary[key], key))
    
    print("\nTop related tokens (via embeddings):\n")
    local_hash_emb = {}  # used to not show same token 2x (linked to 2 different words) 
    q_embeddings = dict(sorted(q_embeddings.items(),
                               key=lambda item: item[1],
                               reverse=True))
    
    doc_embeddings = []
    # Logic for retrieving embeddings
    
    for key in q_embeddings:
        word = key[0]
        token = key[1]
        pmi = q_embeddings[key]
        
        if token not in local_hash_emb:        
            doc_embeddings.append({
                "word": word,
                "token": token,
                "pmi": pmi
            })  
    
    docs = []
    print("\nFull content sorted by relevancy\n")
    n_ID = 0
    for ID in ID_score_ranked:
        content = ID_to_content[ID]
        rankx = ID_score_ranked[ID]
        size = ID_size[ID]
        if n_ID < nresults and size < 60000:
            print("%8s %3d %5d %s %s\n" %(ID, rankx, size, ID_hash[ID], content))
            docs.append({
                "id": ID,
                # "agent":list(ID_to_agents[ID].keys())[0] if ID in ID_to_agents else "",
                "agents": ", ".join(list(exllm.get_value(ID, ID_to_agents))),
                # "category":result_dict["category_text"],
                # "title":result_dict["title_text"],
                # "tags": ", ".join([tag.strip() for tag in result_dict['tags_list_text']]),
                # "description":result_dict["description_text"],
                # "modified_date":datetime.strptime(
                #     result_dict["Modified Date"], 
                #     "%Y-%m-%dT%H:%M:%S.%fZ"
                #     ).strftime("%Y-%m-%d %I:%M %p") if "Modified Date" in result_dict else "",
                # "link_list_text": result_dict["link_list_text"] if "link_list_text" in result_dict else "",
                # "likes_list_text": result_dict["likes_list_text"] if "likes_list_text" in result_dict else "", 
                # "raw_text": item.split("~~")[1]           
                "content": content,
                "rank": rankx,
                "size": size,
                "hash_id": ID_hash[ID]
            })
        n_ID += 1
    complete_raw_content = " ".join([doc["content"]["description_text"] for doc in docs])
    question = form_params['queryText']
    processed_content = parse_docs(complete_raw_content, question)
    print(f"Processed content: {processed_content}")
    complete_content = processed_content
    return {"embeddings": doc_embeddings, "docs": docs, "complete_content": complete_content}
