import streamlit as st
from rag import process_urls, generate_answer

st.set_page_config(page_title="Real Estate Research Tool")
st.title("🏠 Real Estate Research Tool")

# Sidebar URL inputs
st.sidebar.header("Enter URLs to process")
url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")

# Placeholders for feedback
url_status_placeholder = st.empty()
query_placeholder = st.empty()

# Flag to check if URLs have been processed
urls_processed = False

# Process URLs button
if st.sidebar.button("Process URLs"):
    urls = [url for url in (url1, url2, url3) if url.strip() != ""]
    if not urls:
        url_status_placeholder.warning("❌ You must provide at least one valid URL")
    else:
        with st.spinner("Processing URLs..."):
            for status in process_urls(urls):
                st.write(status)
        urls_processed = True
        st.success("✅ URLs processed successfully!")

# Query input
query = st.text_input("Ask a question about the URLs:")
if query:
    if not urls_processed:
        query_placeholder.warning("⚠️ You must process URLs first!")
    else:
        with st.spinner("Generating answer..."):
            try:
                answer, sources = generate_answer(query)
                st.header("Answer:")
                st.write(answer)

                if sources:
                    st.subheader("Sources:")
                    for source in sources.split("\n"):
                        st.write(f"- {source}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
