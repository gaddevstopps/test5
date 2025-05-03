import streamlit as st
from serpapi import GoogleSearch
import time

st.title("Ad-Spending Business Finder (Debug Mode)")

# Input fields
business_type = st.text_input("Business Type (e.g., HVAC, landscaper)", "")
city = st.text_input("City and State (e.g., San Diego, CA)", "")
api_key = st.secrets["serpapi_key"]

if business_type and city:
    st.info("Scraping Google Maps...")

    # Prep query
    query = f"{business_type} in {city}"
    all_results = []
    page = 0
    has_next = True

    while has_next:
        st.write(f"Scraping page {page + 1}...")

        params = {
            "engine": "google_maps",
            "type": "search",
            "q": query,
            "api_key": api_key,
            "start": page * 20,
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        local_results = results.get("local_results", [])

        st.write(f"Found {len(local_results)} results on page {page + 1}")
        st.write(results)  # Debug output of full response

        if not local_results:
            break

        all_results.extend(local_results)
        page += 1
        has_next = "serpapi_pagination" in results

        time.sleep(1.5)

    st.write(f"**Total businesses scraped:** {len(all_results)}")

    with_websites = [b for b in all_results if "website" in b]
    st.write(f"**Businesses with websites:** {len(with_websites)}")

    advertised = []
    for idx, biz in enumerate(with_websites):
        domain = biz["website"].replace("https://", "").replace("http://", "").split("/")[0]
        st.write(f"Checking ads for {domain} ({idx + 1} of {len(with_websites)})")

        ad_params = {
            "engine": "google_ads_transparency",
            "q": domain,
            "api_key": api_key
        }

        ad_search = GoogleSearch(ad_params)
        ad_data = ad_search.get_dict()

        st.write(ad_data)  # Debug output of ad check

        if "ad_data" in ad_data and ad_data["ad_data"]:
            advertised.append({
                "name": biz.get("title"),
                "website": biz.get("website"),
                "domain": domain
            })

        time.sleep(1.5)

    st.write(f"**Advertisers found in last 30 days:** {len(advertised)}")

    if advertised:
        st.dataframe(advertised)
    else:
        st.warning("No advertisers found recently.")
