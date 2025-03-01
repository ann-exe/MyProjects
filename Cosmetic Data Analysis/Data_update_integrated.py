from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import pandas as pd
from urllib3.exceptions import ReadTimeoutError
from pymongo import MongoClient
import json
import datetime

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(10)

tabs_links = []
ingredients_links = []

ingredients_dict = {}
ingredients_dicts_list = []

failed_links = []

try:
    site = "https://incibeauty.com/en/ingredients"
    driver.get(site)

    xpath = "//button[@class='fc-button fc-cta-consent fc-primary-button']"
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, xpath))).click()

    xpath = "//ul[@class='list-inline filter-alphanum']//li//a"
    tabs = driver.find_elements(By.XPATH, xpath)
    tabs_links = [element.get_attribute("href") for element in tabs]
    # print(tabs_links)

    for link in tabs_links:
        site = link
        driver.get(site)

        xpath = "//a[@class='color-inherit']"
        WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.XPATH, xpath)))

        ingredients = driver.find_elements(By.XPATH, xpath)
        ingredients_links_list = [element.get_attribute("href") for element in ingredients]
        for ing_link in ingredients_links_list:
            ingredients_links.append(ing_link)

        # print(ingredients_links)

    for index, link in enumerate(ingredients_links):

        if index % 20 == 0 and index != 0:
            driver.quit()
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(10)

        retry = 3
        while retry > 0:
            try:
                site = link
                driver.get(site)
                time.sleep(2)

                xpath = "//ul[@class='list-unstyled']//li"
                WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.XPATH, xpath)))

                general_info = driver.find_elements(By.XPATH, xpath)
                general_info_values = [element.text for element in general_info]
                # print(general_info_values)

                for i in range(len(general_info_values)):
                    try:
                        key, value = general_info_values[i].split(":", 1)
                        ingredients_dict[key] = value.strip()
                    except ValueError:
                        print(f"Skipping item due to split issue: {general_info_values[i]}")

                xpath = "//span[@class='align-middle']"
                penalty_info = driver.find_elements(By.XPATH, xpath)
                penalty_info_values = [element.text for element in penalty_info]
                key, value = "Penalty", ", ".join(penalty_info_values)
                ingredients_dict[key] = value

                xpath = "//ul[@class='fonctions-inci']//li"
                functions_info = driver.find_elements(By.XPATH, xpath)
                functions_info_values = [element.text for element in functions_info]
                # print(functions_info_values)
                key, value = "Functions", functions_info_values
                ingredients_dict[key] = value
                print(ingredients_dict)

                ingredients_dicts_list.append(ingredients_dict.copy())
                ingredients_dict.clear()

                retry = 0

            except ReadTimeoutError:
                retry -= 1
                print(f"Error loading {site}, {retry} attempts left")
                if retry == 0:
                    print(f"Failed to load {site}")
                    failed_links.append(site)

finally:
    print(":)")
    print("Failed links: ", failed_links)
    driver.quit()

ingredients_df = pd.DataFrame(ingredients_dicts_list)
ingredients_df.to_csv("updated_ingredients_scraped_csv.csv", index=False)
ingredients_df.to_json("updated_ingredients_scraped_json.json", orient="records", indent=4, force_ascii=False)

#######################################################################################################################

ingredients_data = "updated_ingredients_scraped_json.json"
ingredients_df = pd.read_json(ingredients_data)

ingredients_columns = ["INCI name", "Classification", "Penalty", "Functions", "Origin(s)"]
ingredients_df = ingredients_df[ingredients_columns]

ingredients_df = ingredients_df.rename(columns={"Origin(s)": "Origin"})


def to_list(txt):
    if txt is None:
        return []
    else:
        txt_list = [x.strip() for x in txt.split(",")]
    return txt_list


def preprocessing_text(txt):
    if txt is None:
        return "Not available"
    txt = txt.replace("\"", "").replace(".", "").replace(" :,", ":")
    return txt


def preprocessing_text_list(txt_list):
    while "" in txt_list:
        txt_list.remove("")
    else:
        for txt_index in range(len(txt_list)):
            txt = txt_list[txt_index]
            txt = txt.replace(".", "").replace(" : ", ": ")
            txt_list[txt_index] = txt
    return txt_list


def preprocessing_penalty(txt):
    if txt == "Strong penalty in all categories":
        return {"Hair penalty": "Strong", "Body penalty": "Strong", "Face penalty": "Strong",
                "Oral cavity penalty": "Strong", "Makeup penalty": "Strong", "Babies penalty": "Strong"}
    elif txt == "Low penalty in all categories":
        return {"Hair penalty": "Low", "Body penalty": "Low", "Face penalty": "Low", "Oral cavity penalty": "Low",
                "Makeup penalty": "Low", "Babies penalty": "Low"}
    elif txt == "No penalty in all categories":
        return {"Hair penalty": "None", "Body penalty": "None", "Face penalty": "None", "Oral cavity penalty": "None",
                "Makeup penalty": "None", "Babies penalty": "None"}
    elif txt == "Medium penalty in all categories":
        return {"Hair penalty": "Medium", "Body penalty": "Medium", "Face penalty": "Medium",
                "Oral cavity penalty": "Medium", "Makeup penalty": "Medium", "Babies penalty": "Medium"}
    elif txt == "Strong penalty in the following categories: Hair colouring, Low penalty in all other categories":
        return {"Hair penalty": "Strong", "Body penalty": "Low", "Face penalty": "Low", "Oral cavity penalty": "Low",
                "Makeup penalty": "Low", "Babies penalty": "Low"}
    elif txt == ("Strong penalty in the following categories: Breath, Children toothpaste, Adult toothpaste, "
                 "Cream for braces, Children toothbrush, Adult toothbrush, Anti-stain and teeth whitening, "
                 "Solid toothpaste, Low penalty in all other categories, Penalised in lip products, "
                 "Penalised in loose make-up powders, Penalized in spray products"):
        return {"Hair penalty": "Low", "Body penalty": "Low", "Face penalty": "Low", "Oral cavity penalty": "Strong",
                "Makeup penalty": "Strong", "Babies penalty": "Low"}
    elif txt == "Low penalty in all categories, Prohibited in spray cosmetics":
        return {"Hair penalty": "Low", "Body penalty": "Low", "Face penalty": "Low", "Oral cavity penalty": "Low",
                "Makeup penalty": "Low", "Babies penalty": "Low"}
    elif txt == "Medium penalty in all categories, Avoid in children under 3 years old":
        return {"Hair penalty": "Medium", "Body penalty": "Medium", "Face penalty": "Medium",
                "Oral cavity penalty": "Medium", "Makeup penalty": "Medium", "Babies penalty": "Strong"}
    elif txt == ("Strong penalty in the following categories: Baby bubble bath, Wipes box, Baby set, Baby care set, "
                 "Diaper cream, Baby cleansing water, Baby shower gel and cream, Baby bath oil, Baby massage oil, "
                 "Baby care oil, Nose hygiene, Baby cleansing milk, Baby milk and moisturizer, Baby disinfectant wipes, "
                 "Baby cleaning wipes, Liniment, Baby washing foam, Baby solid soap, Physiological serum, Baby shampoo, "
                 "2-in-1 shampoo and body wash for baby, Milk crust care, First teeth care, Talc and powder, "
                 "Medium penalty in all other categories"):
        return {"Hair penalty": "Medium", "Body penalty": "Medium", "Face penalty": "Medium",
                "Oral cavity penalty": "Medium", "Makeup penalty": "Medium", "Babies penalty": "Strong"}
    elif txt == ("No penalty in the following categories: Baby shower gel and cream, Shower gel, Shaving cream, "
                 "Liquid soap, Shaving soap, Low penalty in all other categories"):
        return {"Hair penalty": "Low", "Body penalty": "None", "Face penalty": "Low",
                "Oral cavity penalty": "Low", "Makeup penalty": "Low", "Babies penalty": "Low"}
    elif txt == ("Strong penalty in the following categories: Breath, Children toothpaste, Adult toothpaste, "
                 "Cream for braces, Mouthwash, Anti-stain and teeth whitening, Solid toothpaste, Baby bubble bath, "
                 "Wipes box, Baby set, Baby care set, Diaper cream, Various baby care, Baby cleansing water, "
                 "Baby shower gel and cream, Baby bath oil, Baby massage oil, Baby care oil, Nose hygiene, "
                 "Baby cleansing milk, Baby milk and moisturizer, Baby cleaning wipes, Liniment, Baby washing foam, "
                 "Baby solid soap, Physiological serum, 2-in-1 shampoo and body wash for baby, Milk crust care, "
                 "First teeth care, Talc and powder, Low penalty in all other categories"):
        return {"Hair penalty": "Low", "Body penalty": "Low", "Face penalty": "Low",
                "Oral cavity penalty": "Strong", "Makeup penalty": "Low", "Babies penalty": "Strong"}
    elif txt == ("No penalty in the following categories: Shaving soap, Solid soap, Baby solid soap, Solid shampoo, "
                 "Low penalty in all other categories"):
        return {"Hair penalty": "Low", "Body penalty": "None", "Face penalty": "Low",
                "Oral cavity penalty": "Low", "Makeup penalty": "Low", "Babies penalty": "Low"}
    elif txt == ("Strong penalty in the following categories: Diaper cream, Various baby care, Talc and powder, "
                 "Sanitary pads, Personal hygiene, Low penalty in all other categories"):
        return {"Hair penalty": "Low", "Body penalty": "Strong", "Face penalty": "Low",
                "Oral cavity penalty": "Low", "Makeup penalty": "Low", "Babies penalty": "Strong"}
    else:
        return {"Hair penalty": "Not available", "Body penalty": "Not available", "Face penalty": "Not available",
                "Oral cavity penalty": "Not available", "Makeup penalty": "Not available",
                "Babies penalty": "Not available"}


ingredients_df["Classification"] = ingredients_df["Classification"].apply(to_list)
ingredients_df["Origin"] = ingredients_df["Origin"].apply(to_list)
ingredients_df["Penalty"] = ingredients_df["Penalty"].apply(preprocessing_text)
ingredients_df["Functions"] = ingredients_df["Functions"].apply(preprocessing_text_list)

new_penalty_columns = ingredients_df["Penalty"].apply(preprocessing_penalty).apply(pd.Series)
ingredients_df = ingredients_df.join(new_penalty_columns)

ingredients_df = ingredients_df[["INCI name", "Hair penalty", "Body penalty", "Face penalty",
                                 "Oral cavity penalty", "Makeup penalty", "Babies penalty", "Classification",
                                 "Functions", "Origin"]]

ingredients_df.to_csv("updated_ingredients_with_penalty_csv.csv", index=False)
ingredients_df.to_json("updated_ingredients_with_penalty_json.json", orient="records", indent=4, force_ascii=False)

#######################################################################################################################

client = MongoClient('localhost', 27017)

engineering_db = client.Engineering
ingredients_collection = engineering_db.Ingredients

old_ingredients = list(ingredients_collection.find())

updated_ingredients_json = "updated_ingredients_with_penalty_json.json"

with open(updated_ingredients_json, "r", encoding="utf-8") as file:
    updated_ingredients = json.load(file)

cleaned_updated_ingredients = [{key: value for key, value in ingredient.items() if value not in (None, "", [])} for
                               ingredient in updated_ingredients]
cleaned_old_ingredients = [{key: value for key, value in ingredient.items() if key not in ("_id", "Date")} for
                           ingredient in old_ingredients]

old_ingredients_names = [old_ing["INCI name"] for old_ing in cleaned_old_ingredients]
updated_ingredients_names = [updated_ing["INCI name"] for updated_ing in cleaned_updated_ingredients]

new_records = []
updated_records = []
same_records = []
deleted_records = []

for updated_ing in cleaned_updated_ingredients:
    updated_ing_name = updated_ing["INCI name"]
    if updated_ing_name in old_ingredients_names:
        for old_ing in cleaned_old_ingredients:
            if old_ing["INCI name"] == updated_ing_name:
                if old_ing == updated_ing:
                    same_records.append(updated_ing)
                else:
                    updated_records.append(updated_ing)
    else:
        new_records.append(updated_ing)

for old_ing in cleaned_old_ingredients:
    if old_ing["INCI name"] not in updated_ingredients_names:
        deleted_records.append(old_ing)

for new_record in new_records:
    new_record["Date"] = datetime.datetime.now(datetime.timezone.utc)
    ingredients_collection.insert_one(new_record)

for updated_record in updated_records:
    updated_record["Date"] = datetime.datetime.now(datetime.timezone.utc)
    ingredients_collection.delete_one({"INCI name": updated_record["INCI name"]})
    ingredients_collection.insert_one(updated_record)

for deleted_record in deleted_records:
    ingredients_collection.delete_one({"INCI name": deleted_record["INCI name"]})

#######################################################################################################################

client = MongoClient('localhost', 27017)

engineering_db = client.Engineering
cosmetics_collection = engineering_db.Cosmetics
ingredients_collection = engineering_db.Ingredients
cosmetics_joined_collection = engineering_db.CosmeticsJoined

cosmetics_joined_collection.update_many({}, {"$set": {"Status": "Archived"}})

pipeline = [
    {
        "$unwind": {
            "path": "$Ingredients"
        }
    },
    {
        "$lookup": {
            "from": "Ingredients",
            "localField": "Ingredients",
            "foreignField": "INCI name",
            "as": "IngredientDetails"
        }
    },
    {
        "$unwind": {
            "path": "$IngredientDetails",
            "preserveNullAndEmptyArrays": True
        }
    },
    {
        "$group": {
            "_id": "$_id",
            "Label": { "$first": "$Label" },
            "Brand": { "$first": "$Brand" },
            "Name": { "$first": "$Name" },
            "Price": { "$first": "$Price" },
            "Rank": { "$first": "$Rank" },
            "Ingredients": {
                "$push": {
                    "Ingredient": "$Ingredients",
                    "Details": "$IngredientDetails"
                }
            },
            "Skin": { "$first": "$Skin" }
        }
    },
    {
        "$unset": "_id"
    },
    {
        "$set": {
            "Date": datetime.datetime.now(datetime.timezone.utc),
            "Status": "Current"
        }
    }
]

results = cosmetics_collection.aggregate(pipeline)

cosmetics_joined_collection.insert_many(results)

cosmetics_joined_collection.update_many({}, {"$unset": {"Ingredients.$[].Details._id": ""}})

#######################################################################################################################

client = MongoClient('localhost', 27017)

engineering_db = client.Engineering
cosmetics_joined_collection = engineering_db.CosmeticsJoined

cosmetics_data = list(cosmetics_joined_collection.find({"Status": "Current"}))
cosmetics_df = pd.DataFrame(cosmetics_data)

def calculate_rating(c_df, penalty_category):
    ingredients_ratings = []
    final_ratings = []

    for _, record in c_df.iterrows():
        ingredients_sum = 0
        ingredients_count = 0
        penalty_added = 1
        strong_penalty = ["Suspected endocrine disruptor", "Formaldehyde liberator", "Forbidden in Europe"]

        customer_rank = record["Rank"]
        cosmetic_ingredients = record["Ingredients"]

        for ingredient in cosmetic_ingredients:
            ingredient_details = ingredient.get("Details", None)

            if ingredient_details:
                penalty = ingredient_details.get(penalty_category, None)

                # not needed because if details don't exist it won't get to this part of code
                if penalty is None:
                    continue

                classification = ingredient_details.get("Classification", [])

                if penalty == "Strong":
                    ingredients_count += 1
                    if any(x in classification for x in strong_penalty):
                        penalty_added = 0
                    else:
                        penalty_added -= 0.5
                elif penalty == "Medium":
                    ingredients_count += 1
                    ingredients_sum += 5
                    penalty_added -= 0.04
                elif penalty == "Low":
                    ingredients_count += 1
                    ingredients_sum += 8
                    penalty_added -= 0.02
                elif penalty == "None":
                    ingredients_count += 1
                    ingredients_sum += 10

        if customer_rank == 0:
            rank_weight = 0
            ingredients_weight = 1
        else:
            customer_rank = (customer_rank - 1) * (10 / 4)
            rank_weight = 0.4
            ingredients_weight = 0.6

        if penalty_added < 0:
            penalty_added = 0

        if ingredients_count != 0:
            ingredients_avg = ingredients_sum / ingredients_count
            ingredients_rating = round(ingredients_avg * penalty_added, 2)
            final_rating = round((ingredients_rating * ingredients_weight) + (customer_rank * rank_weight), 2)
        else:
            ingredients_rating = -10
            final_rating = -10

        ingredients_ratings.append(ingredients_rating)
        final_ratings.append(final_rating)

    return ingredients_ratings, final_ratings


ingredients_ratings_col, final_ratings_col = calculate_rating(cosmetics_df, "Face penalty")

cosmetics_df["Ingredients rating"] = ingredients_ratings_col
cosmetics_df["Final rating"] = final_ratings_col

cosmetics_df.to_csv("updated_cosmetics_rating_csv.csv", index=False)

for index, row in cosmetics_df.iterrows():
    cosmetic_id = row["_id"]
    inserted_value = row["Ingredients rating"]

    cosmetics_joined_collection.update_one(
        {"_id": cosmetic_id},
        {"$set": {"Ingredients rating": inserted_value}}
    )

for index, row in cosmetics_df.iterrows():
    cosmetic_id = row["_id"]
    inserted_value = row["Final rating"]

    cosmetics_joined_collection.update_one(
        {"_id": cosmetic_id},
        {"$set": {"Final rating": inserted_value}}
    )

#######################################################################################################################

client = MongoClient('localhost', 27017)

engineering_db = client.Engineering
cosmetics_joined_collection = engineering_db.CosmeticsJoined

cosmetics_data = list(cosmetics_joined_collection.find())
cosmetics_df = pd.DataFrame(cosmetics_data)

def updated_rating(df):
    new_rating = []
    for _, record in df.iterrows():
        customer_rank = record["Rank"]
        if customer_rank == 0:
            customer_rank = -1
        else:
            customer_rank = round((customer_rank - 1) * (10 / 4), 2)
        new_rating.append(customer_rank)
    return new_rating

user_rating = updated_rating(cosmetics_df)
cosmetics_df["User rating"] = user_rating

for index, row in cosmetics_df.iterrows():
    cosmetic_id = row["_id"]
    inserted_value = row["User rating"]

    cosmetics_joined_collection.update_one(
        {"_id": cosmetic_id},
        {"$set": {"User rating": inserted_value}}
    )

cosmetics_joined_collection.update_many({}, {"$unset": {"Rank": {}}})

#######################################################################################################################

client = MongoClient('localhost', 27017)

engineering_db = client.Engineering
cosmetics_joined_collection = engineering_db.CosmeticsJoined

fields_to_check = ["Skin"]

def clean_empty_fields(collection, fields):
    for field in fields:
        collection.update_many(
            {field: {"$eq": None}},
            {"$set": {field: []}}
        )


clean_empty_fields(cosmetics_joined_collection, fields_to_check)

for document in cosmetics_joined_collection.find():
    new_document = {
        "_id": document["_id"],
        "Label": document["Label"],
        "Brand": document["Brand"],
        "Name": document["Name"],
        "Price": document["Price"],
        "Ingredients": document["Ingredients"],
        "Skin": document["Skin"],
        "User rating": document["User rating"],
        "Ingredients rating": document["Ingredients rating"],
        "Final rating": document["Final rating"],
        "Date": document["Date"],
        "Status": document["Status"]
    }

    cosmetics_joined_collection.replace_one({"_id": document["_id"]}, new_document)

fields_to_check = ["Skin"]

def clean_empty_fields(collection, fields):
    for field in fields:
        collection.update_many(
            {field: {"$eq": []}},
            {"$unset": {field: ""}}
        )

clean_empty_fields(cosmetics_joined_collection, fields_to_check)

fields_to_check = ["User rating"]

def clean_empty_fields(collection, fields):
    for field in fields:
        collection.update_many(
            {field: {"$eq": -1}},
            {"$unset": {field: ""}}
        )


clean_empty_fields(cosmetics_joined_collection, fields_to_check)
