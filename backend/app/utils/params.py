from .types import frontendParamsType
defaultFrontendParams: frontendParamsType = {
    'useStem': False,    
    'beta': 1.0,     
    'queryText': '',    
    'distill': False,
    'maxTokenCount': 500,
    'nresults': 15
}


# import pickle
# from . import functions as exllm

# get_bin = lambda x, n: format(x, 'b').zfill(n)

# ignore = ('data',)

# DATA_DIR = "./app/data"
# # DATAFILE = "backend_tables.pkl"



# sample_queries = (
#     'aws google cloud',
#     'AWS Google cloud',
#     'financial statements 2024',
#     'financial reports 2024',
#     'growth projections data',
#     'growth projections tables',
#     'growth projections picture',
#     'growth projections image',
#     'sales projections',
#     'sales projections gaming',
#     'sales projection games',
#     'investor',
#     'public conference !confer !publication',
#     'conference public~conference call',
#     'public~conference conference~call',
#     'public~conference conference~calls'
# )

# sectionLabels = { 
#     # map section label (in output) to corresponding backend table name
#     'Dict' :'dictionary', 
#     'Pairs':'hash_pairs', 
#     'Category':'hash_context1', 
#     'Tags'  :'hash_context2', 
#     'Titles':'hash_context3', 
#     'Descr.':'hash_context4', 
#     'Meta'  :'hash_context5',
#     'ID'    :'hash_ID',
#     'Agents': 'hash_agents',
#     'Whole' :'full_content'
# }


# tableNames = (
#   'dictionary',     # multitokens (key = multitoken)
#   'ID_to_agents',   # map text entity ID to agents list (key = text entity ID)
#   'embeddings',     # to show related keywords in prompt results (key = multitoken)
#   'sorted_ngrams',  # to build embeddings (key = multitoken),
#   'ID_to_content',  # full content attached to text entity ID (key = text entity ID)
#   'hash_unstem',    # match prompt words to multitokens (key = stemmed word) 
#   'ID_to_index',    # map ID to multi-index (key = text entity ID)
#   'ID_size',        # content size (key = text entity ID)
#   'hash_ID',        # text entity ID table (key = multitoken, value is list of IDs)                
# )
    
# stopwords = ('', '-', 'in', 'the', 'and', 'to', 'of', 'a', 'this', 'for', 'is', 'with', 'from', 
#              'as', 'on', 'an', 'that', 'it', 'are', 'within', 'will', 'by', 'or', 'its', 'can', 
#              'your', 'be','about', 'used', 'our', 'their', 'you', 'into', 'using', 'these', 
#              'which', 'we', 'how', 'see', 'below', 'all', 'use', 'across', 'provide', 'provides',
#              'aims', 'one', '&', 'ensuring', 'crucial', 'at', 'various', 'through', 'find', 'ensure',
#              'more', 'another', 'but', 'should', 'considered', 'provided', 'must', 'whether',
#              'located', 'where', 'begins', 'any', 'what', 'some', 'under', 'does', 'belong',
#              'included', 'part', 'associated')  

# # agent_map key is corpus word, value is agent (many-to-one)
# agent_map = { 'stock': 'Stock',
#               'fiscal 2022': 'Year 2022',
#               'fiscal 2023': 'Year 2023',
#               'income': 'Income',
#               'tax': 'Tax',
#               'cash': 'Cash',
#               'products': 'Products',
#               'revenue': 'Revenue',
#               'directors': 'Directors',
#               'data': 'Data',
#               'equity': 'Equity',
#               'management': 'Management',
#               'common stock': 'Common Stock',
#               'securities': 'Securities',
#               'assets': 'Assests',
#               'financial statements': 'Financial Statements',
#               'restricted stock': 'Restricted Stock',
#               'accelerated computing': 'Accelerated Computing',
#               'data center': 'Data Center',
#               'non-gaap': 'Non-GAAP',
#             }    

# backendTables = {}
# for name in tableNames:
#     backendTables[name] = {}

# for tableName in backendTables:
#     print("reading %16s" %(tableName), end = " ") 
#     filename = f"{DATA_DIR}/backend_{tableName}.txt"
#     if tableName == 'stopwords':
#         backendTables[tableName]  = exllm.read_list(filename)
#     elif tableName in ('dictionary', 'ID_size'): 
#         backendTables[tableName] = exllm.read_pairs(filename)
#     elif tableName in ('hash_stem', ):
#         backendTables[tableName]  = exllm.read_table(filename, format = "str")
#     elif tableName not in ('hash_pairs', 'ctokens'):
#         backendTables[tableName]  = exllm.read_table(filename)
        
# backendTables['stopwords'] = stopwords 