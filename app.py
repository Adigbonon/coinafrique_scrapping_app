import streamlit as st
import pandas as pnd
from bs4 import BeautifulSoup as bs
import requests
import matplotlib.pyplot as plt

urls = {
    "Chiens": "https://sn.coinafrique.com/categorie/chiens",
    "Moutons": "https://sn.coinafrique.com/categorie/moutons",
    "Poules - Lapins - Pigeons": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
    "Autres animaux": "https://sn.coinafrique.com/categorie/autres-animaux"
}

df = pnd.DataFrame()

page_bg_img = """
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1550684656-96eda9e5c632?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align:center;'>COIN AFRIQUE SCRAPING APP🐶</h1>",
    unsafe_allow_html=True
)

st.markdown("""
This application allows you to scrape animals data from Coinafrica, analyze, and download them.\n
**Data source:**
* **url 1:** [CHIENS](https://sn.coinafrique.com/categorie/chiens)
* **url 2:** [MOUTONS](https://sn.coinafrique.com/categorie/moutons)
* **url 3:** [POULES - LAPINS - PIGEONS](https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons)
* **url 4:** [AUTRES ANIMAUX](https://sn.coinafrique.com/categorie/autres-animaux)
""")

st.sidebar.header('SCRAPING OPTIONS')
pages = st.sidebar.selectbox(
    "Number of pages",
    list(range(1, 51)) # on peut scraper jusqu'à 50 pages
)
choice = st.sidebar.selectbox(
    "Options",
    [
        "Scrape data",
        "Download scraped data",
        "Data dashboard",
        "Fill a form to evaluate the app"
    ]
)

def display_data(DF, csv_name):
    st.dataframe(DF)
    st.download_button(
        "Download data as csv",
        DF.to_csv(index=False),
        csv_name,
        "text/csv"
    )


def scrape_animals(url, pages):
    data = []

    for page in range(1, pages + 1):
        response = requests.get(f"{url}?page={page}")
        soup = bs(response.text, "html.parser")

        annonces = soup.find_all("div", class_="col s6 m4 l3")

        for annonce in annonces:

            try:
                nom =  annonce.find("p", class_="ad__card-description").a.text

                prix =  int(annonce.find("p", class_="ad__card-price").a.text.strip().replace("CFA", "").replace(" ", ""))

                adresse = annonce.find("p", class_="ad__card-location").span.text

                image_lien = annonce.find("img", class_="ad__card-img")['src']

                data.append({
                    "nom": nom,
                    "prix": prix,
                    "adresse": adresse,
                    "image_lien": image_lien
                })

            except:
                pass

    return pnd.DataFrame(data)


def scrape_animals_details(url, pages):
    data = []

    for page in range(1, pages + 1):
        response = requests.get(f"{url}?page={page}")
        soup = bs(response.text, "html.parser")

        annonces = soup.find_all("div", class_="ad__card")

        for annonce in annonces:
            try:
                nom =  annonce.find("p", class_="ad__card-description").a.text

                lien = annonce.find("a", href=True)["href"]
                url_detail = "https://sn.coinafrique.com" + lien

                details_page = requests.get(url_detail)
                soup_page = bs(details_page.text, "html.parser")

                box = soup_page.find("div", class_="ad__info__box-descriptions")
                details = box.find_all("p")[1].text.strip() if box else nom

                prix =  int(annonce.find("p", class_="ad__card-price").a.text.strip().replace("CFA", "").replace(" ", ""))

                adresse = annonce.find("p", class_="ad__card-location").span.text

                image_lien = annonce.find("img", class_="ad__card-img")['src']

                data.append({
                    "details": details,
                    "prix": prix,
                    "adresse": adresse,
                    "image_lien": image_lien
                })

            except :
                pass

    return pnd.DataFrame(data)

def clean_animals_data(df, category):
        # Nettoie les données scrapées automatiquement.
        df = df.copy()

        if category == "Poules - Lapins - Pigeons":
            colonnes = ["details", "prix", "adresse", "image_lien"]
            df = df[colonnes]

            df["details"] = df["details"].fillna("Aucune information").str.strip()
        else:
            colonnes = ["nom", "prix", "adresse", "image_lien"]
            df = df[colonnes]
            df["nom"] = df["nom"].fillna("Aucun nom").str.strip()

        # Nettoyage du prix
        df["prix"] = df["prix"].astype(str).str.replace("Prix sur demande", "")
        df["prix"] = df["prix"].str.replace("CFA", "").str.replace(" ", "")
        df["prix"] = pnd.to_numeric(df["prix"], errors="coerce")

        # Nettoyage des autres colonnes
        df["adresse"] = df["adresse"].fillna("Aucune adresse").str.strip()
        df["image_lien"] = df["image_lien"].fillna("Aucun lien").str.strip()

        # Suppression des doublons et des lignes sans prix adresse image
        df.drop_duplicates(inplace=True)
        df = df.dropna(subset=["prix", "adresse", "image_lien"])

        return df

if choice == "Scrape data":

    category = st.selectbox(
        "**Choose a category**",
        ["Select a category", *urls.keys()]
    )

    if category != "Select a category":
        url = urls[category]
        if category == "Poules - Lapins - Pigeons" :
            st.warning("This scraping takes some time; please be patient or reduce the number of pages to scrap (eg: 2)...")
            df = scrape_animals_details(url, pages)
        else :
            df = scrape_animals(url, pages)

        st.success("Scraping ended successfully")
        st.markdown(f"**Total data : {df.shape[0]}**")

        display_data(df, category + ".csv")
    else :
        st.warning("Please choose a category !")

elif choice == "Download scraped data":
    st.subheader("Those are already scrapped data from the coinafrique website with the extension Web Scraper. ")
    st.markdown("The datas are not cleaned. ")

    file = ""

    category = st.selectbox(
        "**Choose a category**",
        ["Select a category", *urls.keys()]
    )

    if category != "Select a category":
        if category == "Chiens":
            file = "coinafrique_chiens_data.csv"
        elif category == "Moutons":
            file = "coinafrique_moutons_data.csv"
        elif category == "Poules - Lapins - Pigeons":
            file = "coinafrique_poules_lapins_pigeons_data.csv"
        elif category == "Autres animaux":
            file = "coinafrique_autres_animaux_data.csv"

        df = pnd.read_csv("web_scrapper_data/" + file)
        if category == "Poules - Lapins - Pigeons":
            df = df[["details", "prix", "adresse", "image_lien"]]
        else :
            df = df[["nom", "prix", "adresse", "image_lien"]]

        display_data(df, category + "_ws.csv")

    else :
        st.warning("Please choose a category !")

elif choice == "Data dashboard":
    category = st.selectbox(
        "**Choose a category**",
        ["Select a category", *urls.keys()]
    )

    if category != "Select a category":
        if category == "Chiens":
            file_raw = "coinafrique_chiens_data.csv"
        elif category == "Moutons":
            file_raw = "coinafrique_moutons_data.csv"
        elif category == "Poules - Lapins - Pigeons":
            file_raw = "coinafrique_poules_lapins_pigeons_data.csv"
        elif category == "Autres animaux":
            file_raw = "coinafrique_autres_animaux_data.csv"

        df = pnd.read_csv("web_scrapper_data/" + file_raw)
        df_clean = clean_animals_data(df, category)

        st.subheader("Some numbers : ")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total data", df_clean.shape[0])
        col2.metric("Average price", int(df_clean["prix"].mean()))
        col3.metric("Minimum price", int(df_clean["prix"].min()))
        col4.metric("Maximum price", int(df_clean["prix"].max()))

        df_clean["ville"] = df_clean["adresse"].str.split(",").str[0]

        st.subheader("Number of ads in each city")
        ads_by_city = df_clean["ville"].value_counts().head(10)
        graph_ads_by_city = plt.figure(figsize=(25, 5))
        plt.bar(ads_by_city.index, ads_by_city.values)
        plt.xlabel("City")
        plt.ylabel("Number of ads")
        plt.title("Top 10 cities by number of ads in each city")
        st.pyplot(graph_ads_by_city)

        st.subheader("Average price by city (Last 10)")
        average_price_by_city = (
            df_clean.groupby("ville")["prix"]
            .mean()
            .sort_values(ascending=False)
            .tail(10)
        )
        graph_average_price_by_city = plt.figure(figsize=(25, 5))
        plt.bar(average_price_by_city.index, average_price_by_city.values)
        plt.xlabel("City")
        plt.ylabel("Average price (CFA)")
        plt.title("Last 10 cities by average price")
        st.pyplot(graph_average_price_by_city)


    else :
        st.warning("Please choose a category !")

elif choice == "Fill a form to evaluate the app":
    st.markdown(
        "<h3 style='text-align:center;'>📋 App Evaluation Form</h3>",
        unsafe_allow_html=True
    )

    left, middle, right = st.columns(3)
    with left:
        st.link_button("Kobo form", "https://ee.kobotoolbox.org/x/OKQlNiqD", width="stretch")

    with right:
            st.link_button("Google form", "https://docs.google.com/forms/d/e/1FAIpQLSfX2cyLWxN8fy9xvWl5Yp8j6cI8OwNI-Y0wlzyhEjsGAX_BTg/viewform?usp=publish-editor", width="stretch")

