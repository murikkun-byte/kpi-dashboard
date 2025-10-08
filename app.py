import streamlit as st
import pandas as pd
import plotly.express as px

# === Настройки страницы ===
st.set_page_config(page_title="KPI Dashboard", layout="wide")
st.title("📊 KPI Dashboard")

st.write("Загрузите Excel-файл с данными KPI, чтобы начать анализ.")

# === 1. Загрузка файла ===
uploaded_file = st.file_uploader("📤 Загрузите файл (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # === 2. Чтение данных ===
    df = pd.read_excel(uploaded_file, sheet_name=0)

    # Упрощаем названия колонок (при необходимости)
    df = df.rename(columns={
        "Ichki audit xizmati xodimlari\nFIO": "FIO",
        "Lavozimi": "Lavozim",
        "Yigʻma koʻrsatkich": "Yigma"
    })

    # Проверяем наличие нужных столбцов
    required_cols = {"FIO", "Lavozim", "Yigma"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ Файл должен содержать столбцы: {', '.join(required_cols)}")
    else:
        # === 3. Подготовка данных ===
        df["Yigma_percent"] = (df["Yigma"] * 100).round(2)

        def categorize(value):
            if value < 56:
                return "Qoniqarsiz"
            elif value < 71:
                return "Qoniqarli"
            elif value < 86:
                return "Yaxshi"
            else:
                return "A’lo"

        df["Baholash"] = df["Yigma_percent"].apply(categorize)

        # === 4. Фильтр по сотруднику ===
        fio = st.selectbox("🔎 Выберите сотрудника:", ["Все"] + list(df["FIO"].unique()))

        if fio != "Все":
            st.dataframe(df[df["FIO"] == fio])
        else:
            st.dataframe(df)

        # === 5. Графики ===
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Топ-10 сотрудников по KPI")

            category = st.selectbox(
                "📌 Выберите категорию:",
                ["Все", "Qoniqarsiz", "Qoniqarli", "Yaxshi", "A’lo"]
            )

            if category == "Все":
                filtered = df.copy()
            else:
                filtered = df[df["Baholash"] == category]

            top10 = filtered.sort_values("Yigma_percent", ascending=False).head(10)

            fig = px.bar(
                top10, x="Yigma_percent", y="FIO", orientation="h",
                color="Baholash", text="Yigma_percent",
                color_discrete_map={
                    "Qoniqarsiz": "red",
                    "Qoniqarli": "yellow",
                    "Yaxshi": "green",
                    "A’lo": "blue"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🍩 Распределение по категориям")
            pie_data = df["Baholash"].value_counts().reset_index()
            pie_data.columns = ["Baholash", "Count"]
            fig2 = px.pie(
                pie_data, values="Count", names="Baholash",
                color="Baholash",
                color_discrete_map={
                    "Qoniqarsiz": "red",
                    "Qoniqarli": "yellow",
                    "Yaxshi": "green",
                    "A’lo": "blue"
                }
            )
            st.plotly_chart(fig2, use_container_width=True)

        # === 6. KPI-метрики ===
        st.subheader("📌 Общие показатели")
        col1, col2, col3 = st.columns(3)

        col1.metric("Количество сотрудников", len(df))
        col2.metric("Средний KPI %", f"{df['Yigma_percent'].mean():.2f}%")
        col3.metric("Доля 'A’lo'", f"{(df['Baholash'].value_counts().get('A’lo', 0)/len(df))*100:.1f}%")

else:
    st.info("⬆️ Пожалуйста, загрузите Excel-файл для отображения данных.")
