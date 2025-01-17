# from .params import (get_bin, ignore, sample_queries, 
#                      sectionLabels, backendTables)
# from .types import frontendParamsType
import nltk
import requests


#--- Stemming
def stem(dictionary):

    from nltk.stem import PorterStemmer
    # from nltk.stem import WordNetLemmatizer  
    stemmer = PorterStemmer()
    # lemmatizer = WordNetLemmatizer() 

    hash_unstem = {}
    for word in dictionary:
        if word.count('~') == 0:  
            key = stemmer.stem(word)
            # key = lemmatizer.lemmatize(word) 
            hash_unstem = update_listHash(hash_unstem, key, word)

    hash_stem = {}
    for key in hash_unstem: 
        list = hash_unstem[key]
        if len(list) > 1:
            # a few stems with 3+ words need breaking down [not done yet]
            # print(key, hash_unstem[key])
            max_cnt = 0
            for word in list:
                cnt = dictionary[word]
                if cnt > max_cnt:
                    max_cnt = cnt
                    lead_word = word 
            for word in list:
                if word != lead_word:
                    hash_stem[word] = lead_word 

    hash_stem = dict(sorted(hash_stem.items()))
    return(hash_stem, hash_unstem)


#--- Read backend-tables

def get_data(filename, path):
    print(f"reading {filename}")
    if 'http' in path: 
        response = requests.get(path + filename)
        data = (response.text).replace('\r','').split("\n")
    else:
        file = open(filename, "r", encoding="latin-1")
        data = [line.rstrip() for line in file.readlines()] 
        file.close()
    return(data)


def read_table(filename, format = "float", path = ''): 
    table = {}
    data = get_data(filename, path)
    for line in data:
        line = line.split('\t')
        if len(line) > 1:
          value = line[1]
          if format == 'str':
              table[line[0]] = line[1]
          else:
              table[line[0]] = eval(line[1])
    return(table)


def read_list(filename, path = ''):
    data = get_data(filename, path)
    stopwords = eval(data[0]) 
    return(stopwords)


def read_pairs(filename, path = ''):
    dictionary = {}
    data = get_data(filename, path)
    for line in data:
        line = line.split('\t')
        if len(line) > 1:
            if type(line[1]) is not float:
                dictionary[line[0]] = float(line[1]) 
            else:
                dictionary[line[0]] = line[1] 
    return(dictionary)


#--- Hash functions 

def update_listHash(hash, key, value):

    if key in hash:
        list = hash[key]
        if value not in list:
            list = (*list, value)
    else:
        list = (value,)
    hash[key] = list
    return(hash)


def update_hash(hash, key, count=1):

    if key in hash:
        hash[key] += count
    else:
        hash[key] = count
    return(hash)


def update_nestedHash(hash, key, value, count=1):

    # 'key' is a word here, value is tuple or single value
    if key in hash:
        local_hash = hash[key]
    else:
        local_hash = {}
    if type(value) is not tuple: 
        value = (value,)
    for item in value:
        if item in local_hash:
            local_hash[item] += count
        else:
            local_hash[item] = count
    hash[key] = local_hash 
    return(hash)


def get_value(key, hash):
    if key in hash:
        value = hash[key]
    else:
        value = ''
    return(value)


#--- Build back-end tables

def update_tables(backendTables, word, hash_crawl, backendParams):

    category     = get_value('category', hash_crawl)
    tag_list     = get_value('tag_list', hash_crawl)
    title        = get_value('title', hash_crawl)
    description  = get_value('description', hash_crawl)  #
    meta         = get_value('meta', hash_crawl)
    ID           = get_value('ID', hash_crawl)
    agents       = get_value('agents', hash_crawl)
    full_content = get_value('full_content', hash_crawl) #
    mindex       = get_value('mindex', hash_crawl)

    ID_size = backendTables['ID_size']
    
    extraWeights = backendParams['extraWeights']
    word = word.lower()  # add stemming
    weight = 1.0  
    flag = ''        
    if word in category:   
        weight += extraWeights['category'] 
        flag = '__'
    if word in tag_list:
        weight += extraWeights['tag_list']
        flag = '__'
    if word in title:
        weight += extraWeights['title']
        flag = '__'
    if word in meta:
        weight += extraWeights['meta']
        flag = '__'

    if flag != '':
        gword = flag + word
        update_nestedHash(backendTables['hash_ID'], gword, ID) 

    update_hash(backendTables['dictionary'], word, weight)
    update_nestedHash(backendTables['hash_context1'], word, category) 
    update_nestedHash(backendTables['hash_context2'], word, tag_list) 
    update_nestedHash(backendTables['hash_context3'], word, title) 
    update_nestedHash(backendTables['hash_context4'], word, ID) # used to be 'description'
    update_nestedHash(backendTables['hash_context5'], word, meta) 
    update_nestedHash(backendTables['hash_ID'], word, ID) 
    update_nestedHash(backendTables['hash_agents'], word, agents) 
    # update_nestedHash(backendTables['full_content'], word, full_content) # takes space, don't nuild?

    if ID not in backendTables['ID_to_content']:
        for agent in agents:
            # new format: listHash; old format: nestedHash
            # update_nestedHash(backendTables['ID_to_agents'], ID, agent) 
            update_listHash(backendTables['ID_to_agents'], ID, agent)
        update_hash(backendTables['ID_to_content'], ID, full_content)
        update_hash(backendTables['ID_to_index'], ID, mindex)
        update_nestedHash(backendTables['Index_to_IDs'], mindex, ID, ID_size[ID])
    
    return(backendTables)

 
def clean_list(value):

    # change string "['a', 'b', ...]" to ('a', 'b', ...)
    value = value.replace("[", "").replace("]","")
    aux = value.split("~")
    value_list = ()
    for val in aux:
       val = val.replace("'","").replace('"',"").lstrip()
       if val != '':
           value_list = (*value_list, val)
    return(value_list)


def get_key_value_pairs(entity):

    # extract key-value pairs from 'entity' (a string)
    entity = entity[1].replace("}",", '")
    flag = False
    entity2 = ""

    for idx in range(len(entity)):
        if entity[idx] == '[':
            flag = True
        elif entity[idx] == ']':
            flag = False
        if flag and entity[idx] == ",":
            entity2 += "~"
        else:
            entity2 += entity[idx]

    entity = entity2
    key_value_pairs = entity.split(", '") 
    return(key_value_pairs)


def update_dict(backendTables, hash_crawl, backendParams):

    max_multitoken = backendParams['max_multitoken'] 
    maxDist  =  backendParams['maxDist']     
    create_hpairs  = backendParams['create_hpairs']
    create_ctokens = backendParams['create_ctokens']
    use_stem   = backendParams['use_stem']


    category = get_value('category', hash_crawl)
    tag_list = get_value('tag_list', hash_crawl)
    title = get_value('title', hash_crawl)
    description = get_value('description', hash_crawl)
    meta = get_value('meta', hash_crawl)

    text = category + "." + str(tag_list) + "." + title + "." + description + "." 
    text = text.replace('/'," ").replace('(',' ').replace(')',' ').replace('?','')
    text = text.replace("'","").replace('"',"").replace('\\n','').replace('!',' ')
    text = text.replace("\\s",'').replace("\\t",'').replace(","," ").replace(":"," ")  
    text = text.replace(";"," ").replace("|"," ").replace("--"," ").replace("  "," ").lower() 
    sentence_separators = ('.',)
    for sep in sentence_separators:
        text = text.replace(sep, '_~')
    text = text.split('_~') 

    hash_pairs = backendTables['hash_pairs']
    ctokens = backendTables['ctokens']
    hash_stem = backendTables['hash_stem']
    stopwords = backendTables['stopwords']
    buffer2 = []

    for sentence in text:

        words = sentence.split(" ")
        offset = 0 
        buffer = []

        for word in words:

            if use_stem and word in hash_stem:     
                word = hash_stem[word] 

            if word not in stopwords: 
                # word is single token
                buffer.append(word)
                buffer2.append(word) 
                update_tables(backendTables, word, hash_crawl, backendParams)

                for k in range(1, max_multitoken):
                    if offset > 0:
                        # word is now multi-token with k+1 tokens
                        word = buffer[offset-k] + "~" + word
                        buffer2.append(word) 
                        update_tables(backendTables, word, hash_crawl, backendParams)

                offset += 1  
         
    if create_hpairs: 

        for k in range(len(buffer2)):

            wordA = buffer2[k]
            lbound = max(0, k-maxDist) # try bigger value for maxDist
            ubound = min(len(buffer2), k+maxDist+1)

            for l in range(lbound, ubound):
                wordB = buffer2[l]
                key = (wordA, wordB)
                if wordA < wordB: 
                    hash_pairs = update_hash(hash_pairs, key) 
                    if create_ctokens and k != l:
                        ctokens = update_hash(ctokens, key)

    return(backendTables)


def default_frontendParams():

    frontendParams = {
                       'distill': False,
                       'maxTokenCount': 1000,  # ignore generic tokens if large enough 
                       'beta': 1.0, # used in text entity relevancy score, try 0.5
                       'nresults': 20,  # max number of chunks to show in results   
                       'use_stem': False, 
                      }
    return(frontendParams)


def distill_frontendTables(q_dictionary, q_embeddings, frontendParams):
    # purge q_dictionary then q_embeddings (frontend tables) 

    maxTokenCount = frontendParams['maxTokenCount']
    local_hash = {}    
    for key in q_dictionary:
        if q_dictionary[key] > maxTokenCount:
            local_hash[key] = 1
    for keyA in q_dictionary:
        for keyB in q_dictionary:
            nA = q_dictionary[keyA]
            nB = q_dictionary[keyB]
            if keyA != keyB:
                if (keyA in keyB and nA == nB) or (keyA in keyB.split('~')):
                    local_hash[keyA] = 1
    for key in local_hash:
        del q_dictionary[key]  

    local_hash = {}    
    for key in q_embeddings: 
        if key[0] not in q_dictionary:
            local_hash[key] = 1
    for key in local_hash:
        del q_embeddings[key] 
  
    return(q_dictionary, q_embeddings)


def add_embedding(q_embeddings, word, embedding): 
    for token in embedding:
        pmi = embedding[token]
        q_embeddings[(word, token)] = float(pmi)
    return(q_embeddings)