import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Digital Archaeology",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Digital Archaeology - Minimal Mode")
st.success("✅ App is loading! If you see this, Streamlit is working.")

st.markdown("---")

# Simple file browser
st.header("📁 Documents")
data_dir = Path("data/raw")
if data_dir.exists():
    files = list(data_dir.glob("*.pdf"))
    st.write(f"Found {len(files)} PDF files")
    for f in files[:10]:
        st.write(f"- {f.name}")
else:
    st.warning("Data directory not found")

st.markdown("---")
st.info("**Status**: Minimal mode active. Full features will load next.")
