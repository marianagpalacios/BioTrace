import streamlit as st
import tempfile
import pandas as pd

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.fasta import read_fasta
from src.stats import summarize_sequences
from src.taxonomy import load_reference_database, best_similarity_match

st.title("eDNA Insight")
st.write("MVP para análise simples de arquivos FASTA.")

uploaded_file = st.file_uploader("Envie um arquivo FASTA", type=["fasta", "fa"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    sequences = read_fasta(temp_path)
    summary = summarize_sequences(sequences)
    database = load_reference_database("data/reference/species_database.csv")

    st.subheader("Estatísticas")
    st.write(f"Número de sequências: {summary["total_sequences"]}")
    st.write(f"Maior sequência: {summary["max_length"]} bp")
    st.write(f"Menor sequência: {summary["min_length"]} bp")
    st.write(f"Comprimento médio: {summary["average_length"]} bp")

    st.subheader("Identificação taxonômica")

    results = []

    for item in sequences:
        match = best_similarity_match(item["sequence"], database)

        results.append({
            "ID": item["id"],
            "Espécie provável": match["species"],
            "Similaridade (%)": match["similarity"]
        })

    df = pd.DataFrame(results)

    st.dataframe(df)

    st.subheader("Resumo por espécie")
    species_count = df["Espécie provável"].value_counts().reset_index()
    species_count.columns = ["Espécie", "Quantidade"]

    st.dataframe(species_count)

    st.subheader("Gráfico de espécies")
    st.bar_chart(species_count.set_index("Espécie"))

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Baixar resultados em CSV",
        data=csv,
        file_name="edna_results.csv",
        mime="text/csv"
    )