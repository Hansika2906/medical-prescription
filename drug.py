import streamlit as st
import pandas as pd
from difflib import get_close_matches

# Load dataset
df = pd.read_csv("interactions.csv")

# All known drugs in dataset
KNOWN = sorted(set(df['drug_a'].str.lower()).union(df['drug_b'].str.lower()))

def canonicalize(name: str):
    """Match user input to closest drug name in dataset."""
    name = name.strip().lower()
    if name in KNOWN:
        return name
    matches = get_close_matches(name, KNOWN, n=1, cutoff=0.8)
    return matches[0] if matches else None

# Streamlit UI
st.title("💊 Drug Interaction Detection System (Demo)")

st.write("Enter a list of drug names separated by commas (e.g., Warfarin, Aspirin, Ibuprofen).")

# Input box
txt = st.text_area("Enter drug names:", "Warfarin, Aspirin")

if st.button("Check Interactions"):
    drugs = [d.strip() for d in txt.split(",") if d.strip()]
    normalized = [canonicalize(d) for d in drugs]
    mapping = {drugs[i]: normalized[i] for i in range(len(drugs))}

    st.subheader("🔎 Drug Name Mapping")
    st.write(mapping)

    results = []
    for i in range(len(normalized)):
        for j in range(i+1, len(normalized)):
            a, b = normalized[i], normalized[j]
            if not a or not b:
                continue
            hit = df[((df['drug_a'].str.lower() == a) & (df['drug_b'].str.lower() == b)) |
                     ((df['drug_a'].str.lower() == b) & (df['drug_b'].str.lower() == a))]
            if not hit.empty:
                for _, row in hit.iterrows():
                    results.append(row)

    if not results:
        st.success("✅ No interactions found in demo dataset.")
    else:
        st.subheader("⚠ Interactions Found")
        for _, row in pd.DataFrame(results).iterrows():
            st.warning(f"{row['drug_a']} + {row['drug_b']} — {row['severity']}")
            st.write(row['description'])
            st.write("Source:", row['source'])