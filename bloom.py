import streamlit as st
import torch
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from transformers import BartTokenizer, BartForConditionalGeneration
# import SessionState


#Initialize Pinecone Index # Set your Pinecone API key
Api_key = "a1a07892-456f-45b1-9694-e13027dc6a8a"
# Connect to Pinecone
pc = Pinecone(api_key=Api_key)

#Initialize Retriever
# set device to GPU if available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# load the retriever model from huggingface model hub
retriever = SentenceTransformer("flax-sentence-embeddings/all_datasets_v3_mpnet-base", device=device)

index_name = "cognitive-levels-3"

# connect to abstractive-question-answering index we created
index = pc.Index(index_name)

#Initialize Generator # load bart tokenizer and model from huggingface
#tokenizer = BartTokenizer.from_pretrained('vblagoje/bart_lfqa')
#generator = BartForConditionalGeneration.from_pretrained('vblagoje/bart_lfqa').to(device)

def query_pinecone(query, top_k):
    # generate embeddings for the query
    xq = retriever.encode([query]).tolist()
    # search pinecone index for context passage with the answer
    xc = index.query(vector=xq, top_k=top_k, include_metadata=True)
    return xc

# def format_query(query, context):
#     formatted_queries = []
    
#     # Iterate over each context match
#     for match in context:
#         try:
#             # Extract metadata and ensure 'answer' field exists and is a string
#             if 'metadata' in match and isinstance(match['metadata'], dict) and 'answer' in match['metadata']:
#                 answer = str(match['metadata']['answer'])  # Convert answer to string
#                 formatted_query = f"question: {query} context: <P> {answer}"
#                 formatted_queries.append(formatted_query)
#             else:
#                 print(f"Warning: Invalid metadata format for context match: {match}")
#         except Exception as e:
#             print(f"Error processing context match: {match}. Error: {e}")

#     # Join all formatted queries into a single string (separated by '\n')
#     return '\n'.join(formatted_queries)

# def generate_answer(query):
#     # tokenize the query to get input_ids
#     inputs = tokenizer([query], max_length=1024, return_tensors="pt", truncation=True).to(device)
#     # use generator to predict output ids
#     ids = generator.generate(inputs["input_ids"], num_beams=4, min_length=50, max_length=250)

#     # use tokenizer to decode the output ids
#     answer = tokenizer.batch_decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
#     return answer

import streamlit as st

# Initialize session state if not already initialized
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'context' not in st.session_state:
    st.session_state.context = []
if 'history' not in st.session_state:
    st.session_state.history = []


def bloom_page():
    query = st.text_input("Enter your question:")

    if query:
        context = query_pinecone(query, top_k=1)
        # if context and "matches" in context:
        #     formatted_query = format_query(query, context["matches"])
        #     answer = generate_answer(formatted_query)
        z=context['matches'][0]['metadata']
        st.write("Answer:", z)

            # Store query and answer in history
        st.session_state.history.append((query, z))
    else:
        st.write("No relevant context found.")

    st.sidebar.header("QUERY HISTORY")
    selection = st.sidebar.selectbox("History👇🏻", [q for q, a in st.session_state.history])

    if selection:
        selected_answer = [a for q, a in st.session_state.history if q == selection]
        if selected_answer:
            # st.write("Selected Query:", selection)
            st.write("Answer:", selected_answer[0])


    for idx, (q, a) in enumerate(st.session_state.history):
        st.sidebar.subheader(f"Q {idx + 1}: {q}")
        # st.sidebar.write("Answer:", a)

if __name__ == "__main__":
    bloom_page()


