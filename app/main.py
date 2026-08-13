import json
from pathlib import Path
import sys
import tempfile

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config import (  # noqa: E402
    DEFAULT_ALLOW_N,
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_TOP_N,
    LOG_FILE_PATH,
    MAX_RANKING_RESULTS,
    MAX_SIMILARITY,
    MIN_SIMILARITY,
    SIMILARITY_STEP,
)
from src.services.analysis_service import (  # noqa: E402
    AnalysisError,
)
from src.services.reproducible_analysis_service import (  # noqa: E402
    analyze_fasta_reproducibly,
)


st.set_page_config(
    page_title="BioTrace",
    page_icon="🌿",
    layout="wide",
)

st.title("🌿 BioTrace")

st.write(
    "MVP para análise de arquivos FASTA com validação, "
    "estatísticas, classificação por banco local "
    "e rastreabilidade."
)


with st.sidebar:
    st.header("Parâmetros da análise")

    min_similarity = st.slider(
        "Limiar mínimo de similaridade (%)",
        min_value=MIN_SIMILARITY,
        max_value=MAX_SIMILARITY,
        value=DEFAULT_MIN_SIMILARITY,
        step=SIMILARITY_STEP,
    )

    allow_n = st.checkbox(
        "Permitir base ambígua N",
        value=DEFAULT_ALLOW_N,
    )

    top_n = st.number_input(
        "Quantidade máxima no ranking",
        min_value=1,
        max_value=MAX_RANKING_RESULTS,
        value=DEFAULT_TOP_N,
        step=1,
    )

    st.caption(
        "A similaridade usa distância de edição "
        "normalizada. Ela considera substituições, "
        "inserções e deleções simples, mas não "
        "substitui um alinhamento biológico."
    )


uploaded_file = st.file_uploader(
    "Envie um arquivo FASTA",
    type=["fasta", "fa", "fna"],
)


if uploaded_file:
    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".fasta",
        ) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name

        progress_bar = st.progress(
            0.0,
            text="Preparando análise...",
        )

        def update_progress(
            value: float,
            message: str,
        ) -> None:
            progress_bar.progress(
                min(max(value, 0.0), 1.0),
                text=message,
            )

        analysis = (
            analyze_fasta_reproducibly(
                file_path=temp_path,
                reference_database_path=(
                    DEFAULT_REFERENCE_DATABASE_PATH
                ),
                min_similarity=min_similarity,
                allow_n=allow_n,
                top_n=int(top_n),
                progress_callback=(
                    update_progress
                ),
            )
        )

    except AnalysisError as error:
        st.error(str(error))
        st.stop()

    except Exception as error:
        st.error(
            f"Não foi possível concluir "
            f"a análise: {error}"
        )
        st.stop()

    finally:
        if temp_path:
            Path(temp_path).unlink(
                missing_ok=True
            )

    valid_count = analysis["valid_count"]
    invalid_count = analysis["invalid_count"]
    total_sequences = analysis["total_sequences"]

    run_manifest = analysis.get(
        "run_manifest"
    )

    if run_manifest:
        with st.expander(
            "Reprodutibilidade da execução"
        ):
            run_columns = st.columns(3)

            run_columns[0].metric(
                "Status",
                run_manifest["status"],
            )

            run_columns[1].metric(
                "BioTrace",
                run_manifest[
                    "software"
                ]["version"],
            )

            run_columns[2].metric(
                "Python",
                run_manifest[
                    "environment"
                ]["python_version"],
            )

            st.markdown(
                "**Run ID**"
            )

            st.code(
                run_manifest["run_id"]
            )

            st.markdown(
                "**Fingerprint da execução**"
            )

            st.code(
                run_manifest[
                    "run_fingerprint"
                ]
            )

            st.markdown(
                "**SHA-256 da entrada**"
            )

            st.code(
                run_manifest[
                    "input"
                ]["sha256"]
            )

            st.markdown(
                "**SHA-256 dos resultados**"
            )

            st.code(
                run_manifest[
                    "result_sha256"
                ]
                or "não disponível"
            )

            parameters = (
                run_manifest[
                    "parameters"
                ]
            )

            st.caption(
                "Parâmetros: "
                f"min_similarity="
                f"{parameters['min_similarity']} | "
                f"allow_n="
                f"{parameters['allow_n']} | "
                f"top_n="
                f"{parameters['top_n']}"
            )

            software = (
                run_manifest[
                    "software"
                ]
            )

            if software[
                "git_dirty"
            ]:
                st.warning(
                    "Esta execução foi realizada "
                    "com alterações locais não "
                    "commitadas. A reprodução "
                    "exata não é garantida."
                )

            manifest_json = (
                json.dumps(
                    run_manifest,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )

            st.download_button(
                label=(
                    "Baixar manifesto "
                    "da execução"
                ),
                data=manifest_json.encode(
                    "utf-8"
                ),
                file_name=(
                    f"biotrace_run_"
                    f"{run_manifest['run_id']}"
                    f".json"
                ),
                mime="application/json",
                key=(
                    "run-manifest-"
                    f"{run_manifest['run_id']}"
                ),
            )

    for warning in analysis.get(
        "reference_warnings",
        [],
    ):
        st.warning(
            f"Banco de referência: {warning}"
        )

    if invalid_count:
        st.error(
            f"{invalid_count} sequência(s) "
            "inválida(s) foram encontrada(s) "
            "e não serão classificadas."
        )

        invalid_df = pd.DataFrame(
            analysis["invalid_sequences"]
        )

        invalid_df["invalid_bases"] = (
            invalid_df["invalid_bases"].apply(
                lambda bases: (
                    ", ".join(bases)
                    if bases
                    else "-"
                )
            )
        )

        invalid_df = invalid_df.rename(
            columns={
                "id": "ID",
                "invalid_bases": (
                    "Bases inválidas"
                ),
                "reason": "Motivo",
            }
        )

        st.dataframe(
            invalid_df,
            use_container_width=True,
            hide_index=True,
        )

    if valid_count == 0:
        st.warning(
            "Nenhuma sequência válida ficou "
            "disponível para análise."
        )
        st.stop()

    st.success(
        f"Análise concluída: {valid_count} "
        f"de {total_sequences} sequência(s) "
        "analisada(s)."
    )

    overview_columns = st.columns(4)

    overview_columns[0].metric(
        "Recebidas",
        total_sequences,
    )

    overview_columns[1].metric(
        "Analisadas",
        valid_count,
    )

    overview_columns[2].metric(
        "Inválidas",
        invalid_count,
    )

    overview_columns[3].metric(
        "Tempo de execução",
        f"{analysis['execution_time_seconds']:.3f} s",
    )

    summary = analysis["summary"]

    st.subheader(
        "Estatísticas de comprimento"
    )

    length_columns = st.columns(5)

    length_columns[0].metric(
        "Menor",
        f"{summary['min_length']} bp",
    )

    length_columns[1].metric(
        "Maior",
        f"{summary['max_length']} bp",
    )

    length_columns[2].metric(
        "Média",
        f"{summary['average_length']} bp",
    )

    length_columns[3].metric(
        "Mediana",
        f"{summary['median_length']} bp",
    )

    length_columns[4].metric(
        "Desvio padrão",
        f"{summary['length_std_dev']} bp",
    )

    st.subheader(
        "Composição nucleotídica agregada"
    )

    composition_columns = st.columns(6)

    composition_columns[0].metric(
        "A (%)",
        summary["a_frequency"],
    )

    composition_columns[1].metric(
        "T (%)",
        summary["t_frequency"],
    )

    composition_columns[2].metric(
        "C (%)",
        summary["c_frequency"],
    )

    composition_columns[3].metric(
        "G (%)",
        summary["g_frequency"],
    )

    composition_columns[4].metric(
        "AT (%)",
        summary["at_content"],
    )

    composition_columns[5].metric(
        "GC (%)",
        summary["gc_content"],
    )

    metrics_df = pd.DataFrame(
        summary["sequence_metrics"]
    ).rename(
        columns={
            "id": "ID",
            "length": "Comprimento (bp)",
            "a_frequency": "A (%)",
            "t_frequency": "T (%)",
            "c_frequency": "C (%)",
            "g_frequency": "G (%)",
            "at_content": "AT (%)",
            "gc_content": "GC (%)",
            "n_count": "N (bases)",
        }
    )

    st.caption(
        "As frequências usam o comprimento total "
        "como denominador. Quando há N, "
        "A + T + C + G pode ser menor que 100%."
    )

    st.dataframe(
        metrics_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader(
        "Identificação taxonômica"
    )

    results_df = pd.DataFrame(
        analysis["results"]
    )

    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader(
        f"Ranking das {int(top_n)} "
        "melhores correspondências"
    )

    ranking_rows: list[
        dict[str, object]
    ] = []

    for sequence_id, ranking in (
        analysis["rankings"].items()
    ):
        selected_row = results_df.loc[
            results_df["ID"] == sequence_id
        ].iloc[0]

        selected_reference = selected_row[
            "Referência escolhida"
        ]

        ranking_df = pd.DataFrame(
            ranking
        ).rename(
            columns={
                "species": "Espécie",
                "reference_id": "Referência",
                "similarity": (
                    "Similaridade (%)"
                ),
                "gene": "Gene",
                "accession": "Accession",
                "source": "Fonte",
            }
        )

        if not ranking_df.empty:
            ranking_df.insert(
                0,
                "Posição",
                range(
                    1,
                    len(ranking_df) + 1,
                ),
            )

            ranking_df["Escolhida"] = (
                ranking_df["Referência"].apply(
                    lambda reference: (
                        "✅"
                        if reference
                        == selected_reference
                        else ""
                    )
                )
            )

            for row in ranking_df.to_dict(
                orient="records"
            ):
                ranking_rows.append(
                    {
                        "ID da consulta": (
                            sequence_id
                        ),
                        **row,
                    }
                )

        with st.expander(
            f"Sequência {sequence_id}"
        ):
            st.dataframe(
                ranking_df,
                use_container_width=True,
                hide_index=True,
            )

    st.subheader(
        "Resumo por espécie escolhida"
    )

    species_count = (
        results_df["Espécie escolhida"]
        .value_counts()
        .reset_index()
    )

    species_count.columns = [
        "Espécie",
        "Quantidade",
    ]

    st.dataframe(
        species_count,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        species_count.set_index("Espécie")
    )

    with st.expander(
        "Banco de referência e logs"
    ):
        reference_stats = analysis[
            "reference_statistics"
        ]

        reference_columns = st.columns(3)

        reference_columns[0].metric(
            "Referências",
            reference_stats[
                "reference_count"
            ],
        )

        reference_columns[1].metric(
            "Espécies",
            reference_stats[
                "species_count"
            ],
        )

        reference_columns[2].metric(
            "IDs únicos",
            reference_stats[
                "id_count"
            ],
        )

        reference_metadata = analysis.get(
            "reference_metadata"
        )

        if reference_metadata:
            st.markdown(
                "**Proveniência da base curada**"
            )

            provenance_columns = st.columns(
                3
            )

            provenance_columns[0].metric(
                "Versão da base",
                reference_metadata["version"],
            )

            provenance_columns[1].metric(
                "Marcador",
                reference_metadata["marker"],
            )

            provenance_columns[2].metric(
                "Escopo taxonômico",
                reference_metadata[
                    "taxonomic_scope"
                ],
            )

            st.caption(
                "Fonte: "
                f"{reference_metadata['source']} | "
                "Criada em: "
                f"{reference_metadata['created_at']}"
            )

            st.caption(
                "SHA-256 do CSV: "
                f"`{reference_metadata['csv_sha256']}`"
            )

        st.caption(
            f"Arquivo de log: `{LOG_FILE_PATH}`"
        )

    st.subheader("Exportações")

    export_columns = st.columns(3)

    export_columns[0].download_button(
        label="Baixar resultados",
        data=results_df.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="biotrace_results.csv",
        mime="text/csv",
    )

    export_columns[1].download_button(
        label="Baixar estatísticas",
        data=metrics_df.to_csv(
            index=False
        ).encode("utf-8"),
        file_name=(
            "biotrace_sequence_statistics.csv"
        ),
        mime="text/csv",
    )

    ranking_export_df = pd.DataFrame(
        ranking_rows
    )

    export_columns[2].download_button(
        label="Baixar ranking",
        data=ranking_export_df.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="biotrace_rankings.csv",
        mime="text/csv",
    )
