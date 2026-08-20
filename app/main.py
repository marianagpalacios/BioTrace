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
    DEFAULT_FASTQ_MAX_LENGTH,
    DEFAULT_FASTQ_MIN_LENGTH,
    DEFAULT_FASTQ_MIN_MEAN_QUALITY,
    DEFAULT_FASTQ_TRIM_ENDS,
    DEFAULT_FASTQ_TRIM_QUALITY,
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_TOP_N,
    FASTQ_QUALITY_STEP,
    LOG_FILE_PATH,
    MAX_FASTQ_LENGTH,
    MAX_FASTQ_MEAN_QUALITY,
    MAX_FASTQ_TRIM_QUALITY,
    MAX_RANKING_RESULTS,
    MAX_SIMILARITY,
    MIN_FASTQ_LENGTH,
    MIN_FASTQ_MEAN_QUALITY,
    MIN_FASTQ_TRIM_QUALITY,
    MIN_SIMILARITY,
    SIMILARITY_STEP,
)
from src.services.analysis_service import (  # noqa: E402
    AnalysisError,
)
from src.search.blast_backend import (  # noqa: E402
    BlastExecutionError,
    BlastNotInstalledError,
    BlastTimeoutError,
)
from src.reproducibility.hashing import (  # noqa: E402
    sha256_file,
)
from src.services.reproducible_analysis_service import (  # noqa: E402
    analyze_sequence_file_reproducibly,
)


st.set_page_config(
    page_title="BioTrace",
    page_icon="🌿",
    layout="wide",
)

st.title("🌿 BioTrace")

st.write(
    "Análise de arquivos FASTA e FASTQ com validação, "
    "controle de qualidade, busca em banco local, "
    "classificação e rastreabilidade."
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

    search_backend = st.selectbox(
        "Mecanismo de busca",
        options=["pairwise", "blast"],
        format_func=lambda value: (
            "Alinhamento pairwise"
            if value == "pairwise"
            else "BLAST local"
        ),
    )

    search_timeout_seconds = st.number_input(
        "Timeout da busca (s)",
        min_value=1.0,
        value=30.0,
        step=1.0,
    )

    cache_enabled = st.checkbox(
        "Habilitar cache da busca",
        value=True,
    )

    blast_database_path: str | None = None
    blast_database_sha256: str | None = None
    blast_version: str | None = None

    if search_backend == "blast":
        blast_database_path = st.text_input(
            "Banco BLAST",
            value=(
                "tests/data/blast/db/"
                "biotrace_test"
            ),
            help=(
                "Informe o prefixo do banco, "
                "sem extensão."
            ),
        )

        blast_version = st.text_input(
            "Versão do BLAST+",
            value="2.17.0+",
        )

        blast_metadata_path = Path(
            f"{blast_database_path}.metadata.json"
        )

        if blast_metadata_path.exists():
            blast_database_sha256 = sha256_file(
                blast_metadata_path
            )

            st.caption(
                "Integridade do banco registrada "
                "a partir da metadata controlada."
            )

    with st.expander(
        "Controle de qualidade FASTQ"
    ):
        min_mean_quality = st.number_input(
            "Phred médio mínimo",
            min_value=(
                MIN_FASTQ_MEAN_QUALITY
            ),
            max_value=(
                MAX_FASTQ_MEAN_QUALITY
            ),
            value=(
                DEFAULT_FASTQ_MIN_MEAN_QUALITY
            ),
            step=FASTQ_QUALITY_STEP,
        )

        min_read_length = st.number_input(
            "Comprimento mínimo "
            "após QC (bp)",
            min_value=MIN_FASTQ_LENGTH,
            max_value=MAX_FASTQ_LENGTH,
            value=DEFAULT_FASTQ_MIN_LENGTH,
            step=1,
        )

        max_read_length = st.number_input(
            "Comprimento máximo "
            "após QC (bp)",
            min_value=MIN_FASTQ_LENGTH,
            max_value=MAX_FASTQ_LENGTH,
            value=DEFAULT_FASTQ_MAX_LENGTH,
            step=1,
        )

        trim_ends = st.checkbox(
            "Remover bases de baixa "
            "qualidade nas extremidades",
            value=DEFAULT_FASTQ_TRIM_ENDS,
        )

        trim_quality_threshold = (
            st.number_input(
                "Phred mínimo para "
                "trimming das extremidades",
                min_value=(
                    MIN_FASTQ_TRIM_QUALITY
                ),
                max_value=(
                    MAX_FASTQ_TRIM_QUALITY
                ),
                value=(
                    DEFAULT_FASTQ_TRIM_QUALITY
                ),
                step=1,
                disabled=(
                    not trim_ends
                ),
            )
        )

        st.caption(
            "Estes parâmetros são aplicados "
            "somente a FASTQ. Os limites "
            "padrão de comprimento acompanham "
            "o escopo didático COI-5P "
            "do banco atual."
        )

    st.caption(
        "O limiar mínimo é aplicado à identidade "
        "calculada pelo mecanismo de busca selecionado. "
        "Backend de busca: "
        + (
            "BLAST local."
            if search_backend == "blast"
            else "alinhamento pairwise."
        )
    )


uploaded_file = st.file_uploader(
    "Envie um arquivo FASTA ou FASTQ",
    type=[
        "fasta",
        "fa",
        "fna",
        "fastq",
        "fq",
    ],
)


if uploaded_file:
    uploaded_suffix = Path(
        uploaded_file.name
    ).suffix.lower()

    input_format = (
        "fastq"
        if uploaded_suffix
        in {
            ".fastq",
            ".fq",
        }
        else "fasta"
    )

    st.caption(
        f"Arquivo selecionado: `{uploaded_file.name}` | "
        f"Formato detectado: {input_format.upper()} | "
        "Backend de busca: "
        + (
            "BLAST local"
            if search_backend == "blast"
            else "alinhamento pairwise"
        )
    )

    temp_suffix = (
        ".fastq"
        if input_format
        == "fastq"
        else ".fasta"
    )

    if (
        input_format == "fastq"
        and int(
            min_read_length
        )
        > int(
            max_read_length
        )
    ):
        st.error(
            "O comprimento mínimo "
            "não pode ser maior que "
            "o comprimento máximo."
        )

        st.stop()

    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=temp_suffix,
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
            analyze_sequence_file_reproducibly(
                file_path=temp_path,
                input_format=input_format,
                reference_database_path=(
                    DEFAULT_REFERENCE_DATABASE_PATH
                ),
                min_similarity=min_similarity,
                allow_n=allow_n,
                top_n=int(top_n),
                progress_callback=(
                    update_progress
                ),
                min_mean_quality=float(
                    min_mean_quality
                ),
                min_length=int(
                    min_read_length
                ),
                max_length=int(
                    max_read_length
                ),
                trim_ends=trim_ends,
                trim_quality_threshold=int(
                    trim_quality_threshold
                ),
                search_backend=search_backend,
                blast_database_path=(
                    blast_database_path
                ),
                blast_database_sha256=(
                    blast_database_sha256
                ),
                blast_version=blast_version,
                search_timeout_seconds=float(
                    search_timeout_seconds
                ),
                cache_enabled=cache_enabled,
            )
        )

    except BlastNotInstalledError:
        st.error(
            "O NCBI BLAST+ não foi encontrado. "
            "Instale o BLAST+ e confirme que o comando "
            "'blastn' está disponível no PATH."
        )
        st.stop()

    except BlastTimeoutError as error:
        st.error(
            "A busca BLAST excedeu o "
            f"tempo limite: {error}"
        )
        st.stop()

    except BlastExecutionError as error:
        st.error(
            "O BLAST não conseguiu concluir "
            f"a busca: {error}"
        )
        st.stop()

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

        search_parameters = run_manifest[
            "parameters"
        ]

        with st.expander(
            "Mecanismo de busca"
        ):
            backend_name = search_parameters[
                "search_backend"
            ]

            st.metric(
                "Mecanismo de busca",
                (
                    "BLAST local"
                    if backend_name == "blast"
                    else "Alinhamento pairwise"
                ),
            )

            if backend_name == "blast":
                blast_database = (
                    search_parameters[
                        "blast_database_path"
                    ]
                )

                blast_columns = st.columns(4)

                blast_columns[0].metric(
                    "Banco",
                    (
                        Path(blast_database).name
                        if blast_database
                        else "não informado"
                    ),
                )

                blast_columns[1].metric(
                    "BLAST+",
                    search_parameters[
                        "blast_version"
                    ]
                    or "não informado",
                )

                blast_columns[2].metric(
                    "Timeout",
                    (
                        f"{search_parameters['search_timeout_seconds']} s"
                    ),
                )

                blast_columns[3].metric(
                    "Cache",
                    (
                        "habilitado"
                        if search_parameters[
                            "cache_enabled"
                        ]
                        else "desabilitado"
                    ),
                )
            else:
                st.caption(
                    "Backend pairwise com orientação "
                    "e alinhamento biológico local."
                )

    analysis_report = analysis.get(
        "analysis_report"
    )

    if analysis_report:
        with st.expander(
            "Indicadores e relatório da análise",
            expanded=True,
        ):
            indicators = analysis_report[
                "indicators"
            ]
            indicator_columns = st.columns(4)

            indicator_columns[0].metric(
                "Taxa de validação",
                f"{indicators['validation_rate']:.2f}%",
            )
            indicator_columns[1].metric(
                "Taxa de identificação",
                f"{indicators['identification_rate']:.2f}%",
            )
            indicator_columns[2].metric(
                "Espécies observadas",
                analysis_report["taxonomy"][
                    "observed_species_count"
                ],
            )
            indicator_columns[3].metric(
                "Cache hit",
                f"{analysis_report['performance']['cache_hit_rate']:.2f}%",
            )

            search_indicators = analysis_report[
                "search"
            ]
            search_columns = st.columns(4)

            search_columns[0].metric(
                "Identidade média",
                (
                    f"{search_indicators['mean_identity']:.2f}%"
                    if search_indicators["mean_identity"] is not None
                    else "N/A"
                ),
            )
            search_columns[1].metric(
                "Cobertura média",
                (
                    f"{search_indicators['mean_coverage']:.2f}%"
                    if search_indicators["mean_coverage"] is not None
                    else "N/A"
                ),
            )
            search_columns[2].metric(
                "E-value médio",
                search_indicators["mean_evalue"]
                if search_indicators["mean_evalue"] is not None
                else "N/A",
            )
            search_columns[3].metric(
                "Bit score médio",
                search_indicators["mean_bit_score"]
                if search_indicators["mean_bit_score"] is not None
                else "N/A",
            )

            for report_warning in analysis_report.get(
                "warnings",
                [],
            ):
                st.warning(report_warning)

            report_export_paths = analysis.get(
                "report_export_paths",
                {},
            )

            report_downloads = (
                (
                    "analysis_report.json",
                    "Baixar relatório JSON",
                    "application/json",
                ),
                (
                    "analysis_results.csv",
                    "Baixar resultados CSV",
                    "text/csv",
                ),
                (
                    "species_summary.csv",
                    "Baixar resumo por espécie",
                    "text/csv",
                ),
                (
                    "analysis_report.md",
                    "Baixar relatório Markdown",
                    "text/markdown",
                ),
            )
            download_columns = st.columns(4)

            for column, (
                filename,
                label,
                mime,
            ) in zip(
                download_columns,
                report_downloads,
                strict=True,
            ):
                export_path = report_export_paths.get(
                    filename
                )

                if export_path and Path(export_path).exists():
                    column.download_button(
                        label=label,
                        data=Path(export_path).read_bytes(),
                        file_name=filename,
                        mime=mime,
                        key=(
                            f"report-{run_manifest['run_id']}-"
                            f"{filename}"
                        ),
                    )

    for warning in analysis.get(
        "reference_warnings",
        [],
    ):
        st.warning(
            f"Banco de referência: {warning}"
        )

    quality_report_df: (
        pd.DataFrame | None
    ) = None

    if (
        analysis.get(
            "input_format"
        )
        == "fastq"
    ):
        st.subheader(
            "Controle de qualidade FASTQ"
        )

        quality_summary = analysis[
            "quality_summary"
        ]

        quality_columns = st.columns(6)

        quality_columns[0].metric(
            "Reads recebidos",
            quality_summary[
                "total_records"
            ],
        )

        quality_columns[1].metric(
            "Aprovados",
            quality_summary[
                "passed_records"
            ],
        )

        quality_columns[2].metric(
            "Rejeitados",
            quality_summary[
                "rejected_records"
            ],
        )

        quality_columns[3].metric(
            "Bases removidas",
            quality_summary[
                "trimmed_bases"
            ],
        )

        quality_columns[4].metric(
            "Phred médio retido",
            quality_summary[
                "retained_mean_phred"
            ],
        )

        quality_columns[5].metric(
            "Q30 (%)",
            quality_summary[
                "retained_q30_percent"
            ],
        )

        quality_report_df = pd.DataFrame(
            analysis["quality_report"]
        )

        quality_report_df["reasons"] = (
            quality_report_df[
                "reasons"
            ].apply(
                lambda reasons: (
                    " | ".join(reasons)
                    if reasons
                    else "-"
                )
            )
        )

        quality_report_df = (
            quality_report_df.rename(
                columns={
                    "id": "ID",
                    "raw_length": (
                        "Comprimento bruto (bp)"
                    ),
                    "retained_length": (
                        "Comprimento após QC (bp)"
                    ),
                    "trimmed_left": (
                        "Removidas 5'"
                    ),
                    "trimmed_right": (
                        "Removidas 3'"
                    ),
                    "mean_phred": (
                        "Phred médio"
                    ),
                    "min_phred": (
                        "Phred mínimo"
                    ),
                    "max_phred": (
                        "Phred máximo"
                    ),
                    "q20_percent": (
                        "Q20 (%)"
                    ),
                    "q30_percent": (
                        "Q30 (%)"
                    ),
                    "passed": "Aprovado",
                    "reasons": "Motivos",
                }
            )
        )

        st.dataframe(
            quality_report_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="Baixar relatório de QC",
            data=(
                quality_report_df
                .to_csv(index=False)
                .encode("utf-8")
            ),
            file_name=(
                "biotrace_fastq_quality_report.csv"
            ),
            mime="text/csv",
        )

    if invalid_count:
        st.error(
            f"{invalid_count} registro(s) "
            "foram reprovado(s) pela "
            "validação ou pelo controle "
            "de qualidade e não serão "
            "classificados."
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

    preferred_result_columns = [
        "ID",
        "Espécie escolhida",
        "Melhor similaridade (%)",
        "Backend de busca",
        "Identidade do alinhamento (%)",
        "Cobertura do alinhamento (%)",
        "E-value",
        "Bit score",
        "Cache",
    ]

    visible_result_columns = [
        column
        for column in preferred_result_columns
        if column in results_df.columns
    ]

    remaining_result_columns = [
        column
        for column in results_df.columns
        if column not in visible_result_columns
    ]

    results_df = results_df[
        visible_result_columns
        + remaining_result_columns
    ]

    display_results_df = results_df.copy()

    for optional_blast_column in (
        "E-value",
        "Bit score",
    ):
        if optional_blast_column in display_results_df.columns:
            display_results_df[optional_blast_column] = (
                display_results_df[optional_blast_column].apply(
                    lambda value: (
                        "N/A"
                        if pd.isna(value)
                        else value
                    )
                )
            )

    st.dataframe(
        display_results_df,
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
