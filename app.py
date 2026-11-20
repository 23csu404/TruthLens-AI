
import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from extractor import extract_text_from_pdf
from claim_detector import extract_claims
from web_search import search_claim
from verifier import verify_claims_batch


st.set_page_config(
    page_title="TruthLens AI",
    page_icon="🔎",
    layout="wide"
)

# ---------------- HEADER ----------------

st.title("🔎 TruthLens AI")
st.subheader("Turning Documents into Verified Knowledge")

st.write(
    "An AI-powered fact-checking platform that extracts "
    "claims from PDFs, searches live web sources and "
    "evaluates factual accuracy."
)

st.divider()

# ---------------- PDF UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload your PDF document",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("🔍 Fact Check Document", type="primary"):

        # ---------------- TEXT EXTRACTION ----------------

        with st.spinner("Extracting PDF content..."):
            document_text = extract_text_from_pdf(uploaded_file)

        if not document_text:
            st.error("No readable text found in this PDF.")
            st.stop()

        st.success("PDF text extracted successfully!")

        # ---------------- CLAIM EXTRACTION ----------------

        try:
            with st.spinner("Gemini is identifying factual claims..."):
                claims = extract_claims(document_text)

            if not claims:
                st.warning("No verifiable claims were identified.")
                st.stop()

            st.success(f"Identified {len(claims)} factual claims.")

            # ---------------- DOCUMENT SUMMARY ----------------

            st.divider()
            st.header("📄 Document Summary")

            st.write(f"**Document:** {uploaded_file.name}")
            st.write(
                f"**Extracted text:** {len(document_text):,} characters"
            )
            st.write(f"**Factual claims identified:** {len(claims)}")

            st.write(
                "The extracted claims are checked against information "
                "retrieved from live web sources."
            )

            with st.expander("View extracted document text"):
                st.text(document_text)

            # ---------------- PREPARE CLAIMS ----------------

            st.divider()
            st.header("🌐 Live Web Research")

            search_inputs = []

            for index, item in enumerate(claims):

                claim = item.get("claim", "").strip()

                if claim:
                    search_inputs.append({
                        "id": index,
                        "claim": claim,
                        "category": item.get("category", "General"),
                        "importance": item.get(
                            "importance", "Not specified"
                        )
                    })

            if not search_inputs:
                st.warning("No valid claims to verify.")
                st.stop()

            # ---------------- PARALLEL WEB SEARCH ----------------

            evidence_by_id = {}

            progress = st.progress(0)
            status = st.empty()

            max_workers = min(4, len(search_inputs))

            with ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:

                future_map = {
                    executor.submit(
                        search_claim,
                        item["claim"]
                    ): item
                    for item in search_inputs
                }

                completed = 0

                for future in as_completed(future_map):

                    item = future_map[future]

                    try:
                        evidence_by_id[item["id"]] = future.result()

                    except Exception as error:
                        evidence_by_id[item["id"]] = []

                        st.warning(
                            f"Search failed for claim {item['id'] + 1}: "
                            f"{str(error)[:150]}"
                        )

                    completed += 1

                    progress.progress(
                        completed / len(search_inputs)
                    )

                    status.write(
                        f"Web searches completed: "
                        f"{completed}/{len(search_inputs)}"
                    )

            status.success("Live web research completed!")

            # ---------------- BATCH VERIFICATION ----------------

            st.divider()
            st.header("🧠 AI Verification")

            batch_input = []

            for item in search_inputs:

                batch_input.append({
                    "id": item["id"],
                    "claim": item["claim"],
                    "category": item["category"],
                    "importance": item["importance"],
                    "web_evidence": evidence_by_id.get(
                        item["id"], []
                    )
                })

            with st.spinner(
                "Gemini is analysing all claims and evidence together..."
            ):

                try:
                    verification_results = verify_claims_batch(
                        batch_input
                    )

                    verification_by_id = {
                        item["id"]: item
                        for item in verification_results
                    }

                except Exception as error:

                    st.error(
                        "Batch verification could not be completed: "
                        + str(error)[:300]
                    )

                    verification_by_id = {}

            # ---------------- COLLECT RESULTS ----------------

            results = []

            for item in search_inputs:

                claim_id = item["id"]

                verification = verification_by_id.get(
                    claim_id,
                    {
                        "verdict": "Insufficient Evidence",
                        "explanation": (
                            "Verification could not be completed."
                        ),
                        "corrected_fact": "Not established"
                    }
                )

                results.append({
                    "Claim": item["claim"],
                    "Category": item["category"],
                    "Importance": item["importance"],
                    "Verdict": verification.get(
                        "verdict", "Insufficient Evidence"
                    ),
                    "Explanation": verification.get(
                        "explanation", ""
                    ),
                    "Corrected Fact": verification.get(
                        "corrected_fact", ""
                    ),
                    # Preserve Tavily results as the source of truth.
                    "Evidence": evidence_by_id.get(claim_id, [])
                })

            status.empty()

            # ---------------- FACT CHECKING OVERVIEW ----------------

            st.divider()
            st.header("📊 Fact-Checking Overview")

            verdict_types = [
                "Verified",
                "Inaccurate",
                "False",
                "Insufficient Evidence"
            ]

            counts = {
                verdict: sum(
                    1 for result in results
                    if result["Verdict"] == verdict
                )
                for verdict in verdict_types
            }

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Verified", counts["Verified"])
            col2.metric("Inaccurate", counts["Inaccurate"])
            col3.metric("False", counts["False"])
            col4.metric(
                "Insufficient Evidence",
                counts["Insufficient Evidence"]
            )

            st.write(f"**Total claims processed:** {len(results)}")

            # ---------------- DETAILED CLAIM ANALYSIS ----------------

            st.divider()
            st.header("📌 Detailed Claim Analysis")

            for index, result in enumerate(results, start=1):

                with st.expander(
                    f"Claim {index} — {result['Verdict']}"
                ):

                    st.write("**Claim:**", result["Claim"])
                    st.write("**Category:**", result["Category"])
                    st.write("**Importance:**", result["Importance"])
                    st.write("**Verdict:**", result["Verdict"])

                    st.write(
                        "**Explanation:**",
                        result["Explanation"]
                    )

                    st.write(
                        "**Corrected Fact:**",
                        result["Corrected Fact"]
                    )

                    st.write("**Evidence and Sources:**")

                    displayed_urls = set()

                    # Only show source URLs actually returned by Tavily.
                    for source in result["Evidence"]:

                        url = source.get("url", "")
                        title = source.get("title", "Web source")

                        if (
                            url.startswith(("https://", "http://"))
                            and url not in displayed_urls
                        ):

                            st.markdown(f"- [{title}]({url})")
                            displayed_urls.add(url)

                    if not displayed_urls:
                        st.write("No usable web sources were retrieved.")

            # ---------------- CSV EXPORT ----------------

            st.divider()
            st.header("📥 Download Fact-Checking Report")

            report_df = pd.DataFrame([
                {
                    "Claim": result["Claim"],
                    "Category": result["Category"],
                    "Importance": result["Importance"],
                    "Verdict": result["Verdict"],
                    "Explanation": result["Explanation"],
                    "Corrected Fact": result["Corrected Fact"],
                    "Source URLs": "; ".join(
                        source.get("url", "")
                        for source in result["Evidence"]
                        if source.get("url", "").startswith(
                            ("https://", "http://")
                        )
                    )
                }
                for result in results
            ])

            st.download_button(
                "📥 Download CSV Report",
                data=report_df.to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="TruthLens_Fact_Check_Report.csv",
                mime="text/csv"
            )

        except Exception as error:

            st.error("Document processing failed.")
            st.exception(error)

else:

    st.info("Upload a PDF document to begin.")

    st.markdown("""
    **How TruthLens AI works:**

    1. Upload a PDF document.
    2. Extract factual claims using Gemini.
    3. Search the live web using Tavily.
    4. Verify claims against retrieved evidence.
    5. Review verdicts and download the report.
    """)

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "TruthLens AI | Turning Documents into Verified Knowledge"
)
