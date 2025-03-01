import dash
from dash import dcc, html, Input, Output, callback_context
import pandas as pd
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
engineering_db = client.Engineering
cosmetics_joined_collection = engineering_db.CosmeticsJoined
cosmetics_data_current = list(cosmetics_joined_collection.find({"Status": "Current"}))
cosmetics_data_archived = list(cosmetics_joined_collection.find({"Status": "Archived"}))

for item in cosmetics_data_current:
    item["_id"] = str(item["_id"])

cosmetics_current_df = pd.DataFrame(cosmetics_data_current)
cosmetics_archived_df = pd.DataFrame(cosmetics_data_archived)
cosmetics_current_df = cosmetics_current_df[cosmetics_current_df["Final rating"] != -10]
cosmetics_archived_df = cosmetics_archived_df[cosmetics_archived_df["Final rating"] != -10]

unique_labels = sorted(cosmetics_current_df["Label"].unique())
unique_brands = sorted(cosmetics_current_df["Brand"].unique())

unique_skin_types = set()
for skn in cosmetics_current_df["Skin"]:
    if isinstance(skn, list):
        for skin_type in skn:
            unique_skin_types.add(skin_type)
unique_skin_types = sorted(unique_skin_types)

unique_ingredients = set()
for ins_list in cosmetics_current_df["Ingredients"]:
    for ent in ins_list:
        if isinstance(ent, dict) and "Ingredient" in ent:
            unique_ingredients.add(ent["Ingredient"])
        elif isinstance(ent, str):
            unique_ingredients.add(ent)
unique_ingredients = sorted(unique_ingredients)

unique_classifications = set()
for ins in cosmetics_current_df["Ingredients"]:
    if isinstance(ins, list):
        for ent in ins:
            if "Details" in ent and "Classification" in ent["Details"]:
                cls = ent["Details"]["Classification"]
                if isinstance(cls, list):
                    unique_classifications.update(cls)
unique_classifications = sorted(unique_classifications)

unique_functions = set()
for ins in cosmetics_current_df["Ingredients"]:
    if isinstance(ins, list):
        for ent in ins:
            if "Details" in ent and "Functions" in ent["Details"]:
                funcs = ent["Details"]["Functions"]
                if isinstance(funcs, list):
                    cleaned_functions = [f.split(":")[0].strip() for f in funcs]
                    unique_functions.update(cleaned_functions)
unique_functions = sorted(unique_functions)

unique_origins = set()
for ins in cosmetics_current_df["Ingredients"]:
    if isinstance(ins, list):
        for ent in ins:
            if "Details" in ent and "Origin" in ent["Details"]:
                ogs = ent["Details"]["Origin"]
                if isinstance(ogs, list):
                    unique_origins.update(ogs)
unique_origins = sorted(unique_origins)

cosmetic_app = dash.Dash(__name__, suppress_callback_exceptions=True)

def cosmetics_screen():
    return html.Div([
        html.H1("Cosmetics Visualisation", style={"position": "absolute", "top": "50px", "left": "110px"}),

        html.Div([
            html.Button(
                "Cosmetics",
                id="cosmetics-button",
                style={"flex": "1", "padding": "20px", "fontSize": "16px", "border": "0px",
                       "borderRight": "1px solid grey", "borderRadius": "5px 0 0 5px", "fontWeight": "bold",
                       "backgroundColor": "#DDDFF8", "cursor": "pointer"
                       }
            ),
            html.Button(
                "Ingredients",
                id="ingredients-button",
                style={"flex": "1", "padding": "20px", "fontSize": "16px", "border": "0px",
                       "borderLeft": "1px solid grey", "borderRadius": "0 5px 5px 0", "fontWeight": "bold",
                       "cursor": "pointer"}
            )
        ],
        style={"width": "45%", "margin": "60px auto 20px auto", "display": "flex"}
        ),

        html.Div(
            dcc.Input(
                id="search-box-cosmetics",
                type="text",
                placeholder="Search by name or brand...",
                style={"width": "97.5%", "padding": "10px", "fontSize": "16px", "border": "1px solid grey",
                       "borderRadius": "5px"}
            ),
            style={"width": "45%", "margin": "0 auto"}
        ),

        html.Div([
            html.Div([
                html.H3("Filters"),
                html.Div([
                    html.H4("Cosmetic category", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="cosmetic-filter-category",
                        options=[{"label": "Face", "value": "Face"},
                                 {"label": "Body", "value": "Body", "disabled": True},
                                 {"label": "Hair", "value": "Hair", "disabled": True},
                                 {"label": "Oral cavity", "value": "Oral cavity", "disabled": True},
                                 {"label": "Makeup", "value": "Makeup", "disabled": True},
                                 {"label": "Babies", "value": "Babies", "disabled": True}],
                        multi=False,
                        #clearable=False,
                        value="Face",
                        placeholder="Select category...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
                html.Div([
                    html.H4("Cosmetic subcategory", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="cosmetic-filter-subcategory",
                        options=[{"label": label, "value": label} for label in unique_labels],
                        multi=False,
                        placeholder="Select subcategory...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
                html.Div([
                    html.H4("Cosmetic brand", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="cosmetic-filter-brand",
                        options=[{"label": brand, "value": brand} for brand in unique_brands],
                        multi=True,
                        placeholder="Select preferred cosmetic brand...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
                html.Div([
                    html.H4("Skin type", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="cosmetic-filter-skin",
                        options=[{"label": s_type, "value": s_type} for s_type in unique_skin_types],
                        multi=True,
                        placeholder="Select your skin type...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
                html.Div([
                    html.H4("Include ingredients", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="ingredient-filter-include",
                        options=[{"label": ing, "value": ing} for ing in unique_ingredients],
                        multi=True,
                        placeholder="Select ingredients...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
                html.Div([
                    html.H4("Exclude ingredients", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="ingredient-filter-exclude",
                        options=[{"label": ing, "value": ing} for ing in unique_ingredients],
                        multi=True,
                        placeholder="Select ingredients...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
                html.Div([
                    html.H4("Doesn't contain ingredients classified in",
                            style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="ingredient-filter-classified",
                        options=[{"label": ing_class, "value": ing_class} for ing_class in unique_classifications],
                        multi=True,
                        placeholder="Select classification...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
            ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "gap": "10px",
                    "width": "20%",
                    "height": "600px",
                    "margin": "10px 0 0 50px",
                    "padding": "0 5px 0 5px",
                    "borderRadius": "8px",
                    "boxShadow": "3px 3px 5px gray",
                    "backgroundColor": "#DDDFF8"}
            ),
            html.Div([
                html.H3("Sort by:"),
                dcc.Dropdown(
                    id="cosmetics-sort",
                    options=[
                        {"label": "Final Rating Ascending", "value": "Final Rating Ascending"},
                        {"label": "Final Rating Descending", "value": "Final Rating Descending"},
                        {"label": "Price Ascending", "value": "Price Ascending"},
                        {"label": "Price Descending", "value": "Price Descending"}
                    ],
                    value="Final Rating Descending",
                    clearable=False,
                    style={"width": "230px", "fontSize": "16px", "cursor": "pointer"}
                )
            ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "justifyContent": "flex-end",
                    "margin": "10px 100px 20px 0"
                }
            ),
        ],
            style={
                "display": "flex",
                "alignItems": "start",
                "padding": "20px",
                "gap": "1000px"
            }
        ),

        html.Div(
            id="cosmetics-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "width": "1235px",
                "height": "auto",
                "gap": "20px",
                "padding": "20px",
                "position": "absolute",
                "top": "280px",
                "left": "510px"
            }
        ),

        html.Div(
            [
                html.Button("Previous", id="prev-page-button-cosmetics", n_clicks=0),
                dcc.Input(
                    id="current-page-cosmetics",
                    type="number",
                    value=1,
                    min=1,
                    style={"width": "50px", "margin": "0 10px"}
                ),
                html.Span(id="total-pages-cosmetics", style={"marginRight": "10px"}),
                html.Button("Next", id="next-page-button-cosmetics", n_clicks=0),
            ],
            style={"position": "absolute", "top": "230px", "left": "530px"},
        )
    ])

@cosmetic_app.callback(
    [
        Output("cosmetics-grid", "children"),
        Output("total-pages-cosmetics", "children"),
        Output("current-page-cosmetics", "value")
    ],
    [
        Input("search-box-cosmetics", "value"),
        Input("cosmetic-filter-subcategory", "value"),
        Input("cosmetic-filter-brand", "value"),
        Input("cosmetic-filter-skin", "value"),
        Input("ingredient-filter-include", "value"),
        Input("ingredient-filter-exclude", "value"),
        Input("ingredient-filter-classified", "value"),
        Input("cosmetics-sort", "value"),
        Input("current-page-cosmetics", "value"),
        Input("prev-page-button-cosmetics", "n_clicks"),
        Input("next-page-button-cosmetics", "n_clicks")
    ]
)
def update_cosmetic_grid(search_value, subcategory_value, brand_value, skin_value, include_value, exclude_value,
                         classified_value, sort_value, current_page, prev_clicks, next_clicks):

    _ = prev_clicks, next_clicks

    cosmetic_data = cosmetics_current_df.copy()

    if search_value:
        search_value = search_value.lower()
        cosmetic_data = cosmetic_data[
            cosmetic_data["Name"].str.lower().str.contains(search_value, na=False) |
            cosmetic_data["Brand"].str.lower().str.contains(search_value, na=False)
            ]

    if subcategory_value:
        cosmetic_data = cosmetic_data[cosmetic_data["Label"] == subcategory_value]

    if brand_value:
        cosmetic_data = cosmetic_data[cosmetic_data["Brand"].isin(brand_value)]

    if skin_value:
        cosmetic_data = cosmetic_data[
            cosmetic_data["Skin"].apply(
                lambda skins: any(skin in skins for skin in skin_value) if isinstance(skins, list) else False)
        ]

    if include_value:
        cosmetic_data = cosmetic_data[
            cosmetic_data["Ingredients"].apply(
                lambda ingredients: all(
                    ing in [i.get("Ingredient", "") for i in ingredients if isinstance(i, dict)] for ing in
                    include_value)
            )
        ]

    if exclude_value:
        cosmetic_data = cosmetic_data[
            cosmetic_data["Ingredients"].apply(
                lambda ingredients: all(
                    ing not in [i.get("Ingredient", "") for i in ingredients if isinstance(i, dict)] for ing in
                    exclude_value)
            )
        ]

    if classified_value:
        cosmetic_data = cosmetic_data[
            cosmetic_data["Ingredients"].apply(
                lambda ingredients: all(
                    not any(c in classified_value for c in i.get("Details", {}).get("Classification", []))
                    for i in ingredients if isinstance(i, dict)
                )
            )
        ]

    if sort_value:
        if sort_value == "Final Rating Ascending":
            cosmetic_data = cosmetic_data.sort_values("Final rating", ascending=True)
        elif sort_value == "Final Rating Descending":
            cosmetic_data = cosmetic_data.sort_values("Final rating", ascending=False)
        elif sort_value == "Price Ascending":
            cosmetic_data = cosmetic_data.sort_values("Price", ascending=True)
        elif sort_value == "Price Descending":
            cosmetic_data = cosmetic_data.sort_values("Price", ascending=False)

    items_per_page = 30
    total_items = len(cosmetic_data)
    total_pages = max(1, -(-total_items // items_per_page))

    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "prev-page-button-cosmetics" and current_page > 1:
        current_page -= 1
    elif triggered_id == "next-page-button-cosmetics" and current_page < total_pages:
        current_page += 1

    start_index = (current_page - 1) * items_per_page
    end_index = start_index + items_per_page

    page_data = cosmetic_data.iloc[start_index:end_index]

    cards = [
        html.Div([
            dcc.Link(html.H3(row["Name"], style={"fontSize": "18px", "marginBottom": "10px"}),
                     href=f"/cosmetic-details/{row['_id']}", style={"color": "#212046"}),
            html.P(f"Brand: {row['Brand']}"),
            html.P(f"Category: Face"),
            html.P(f"Subcategory: {row['Label']}"),
            html.P(f"Price: ${row['Price']}"),
            html.P(f"Final Rating: {row['Final rating']}"),
        ], style={"border": "1px solid #ccc", "padding": "15px", "borderRadius": "5px", "margin": "0 0 10px 0",
                  "backgroundColor": "#F5F2FB"})
        for _, row in page_data.iterrows()
    ]

    return cards, f"of {total_pages} pages", current_page

def ingredients_screen():
    return html.Div([
        html.H1("Ingredients Visualisation", style={"position": "absolute", "top": "50px", "left": "110px"}),

        html.Div([
            html.Button(
                "Cosmetics",
                id="cosmetics-button",
                style={"flex": "1", "padding": "20px", "fontSize": "16px", "border": "0px",
                       "borderRight": "1px solid grey", "borderRadius": "5px 0 0 5px", "fontWeight": "bold",
                       "cursor": "pointer"
                       }
            ),
            html.Button(
                "Ingredients",
                id="ingredients-button",
                style={"flex": "1", "padding": "20px", "fontSize": "16px", "border": "0px",
                       "borderLeft": "1px solid grey", "borderRadius": "0 5px 5px 0", "fontWeight": "bold",
                       "backgroundColor": "#DDDFF8", "cursor": "pointer"}
            )
        ],
            style={"width": "45%", "margin": "60px auto 20px auto", "display": "flex"}
        ),

        html.Div(
            dcc.Input(
                id="search-box-ingredients",
                type="text",
                placeholder="Search by name...",
                style={"width": "97.5%", "padding": "10px", "fontSize": "16px", "border": "1px solid grey",
                       "borderRadius": "5px"}
            ),
            style={"width": "45%", "margin": "0 auto"}
        ),

        html.Div([
            html.Div([
                html.H3("Filters"),
                html.Div([
                    html.H4("Ingredient classification", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="ingredient-filter-classification",
                        options=[{"label": ing_class, "value": ing_class} for ing_class in unique_classifications],
                        multi=True,
                        placeholder="Select classification...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
                html.Div([
                    html.H4("Ingredient functions", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="ingredient-filter-functions",
                        options=[{"label": func, "value": func} for func in unique_functions],
                        multi=True,
                        placeholder="Select functions...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
                html.Div([
                    html.H4("Ingredient origin", style={"textAlign": "left", "margin": "0 0 5px 3px"}),
                    dcc.Dropdown(
                        id="ingredient-filter-origin",
                        options=[{"label": origin, "value": origin} for origin in unique_origins],
                        multi=True,
                        placeholder="Select origin...",
                        style={"width": "100%", "fontSize": "16px"},
                    )
                ], style={"width": "100%"}),
            ],
                style={
                    "display": "flex",
                    "flex-direction": "column",
                    "alignItems": "center",
                    "gap": "10px",
                    "width": "20%",
                    "height": "330px",
                    "margin": "10px 0 0 50px",
                    "padding": "0 5px 0 5px",
                    "borderRadius": "8px",
                    "boxShadow": "3px 3px 5px gray",
                    "backgroundColor": "#DDDFF8"}
            ),
            html.Div([
                html.H3("Sort by:"),
                dcc.Dropdown(
                    id="ingredients-sort",
                    options=[
                        {"label": "Average Final Rating Ascending", "value": "Average Final Rating Ascending"},
                        {"label": "Average Final Rating Descending", "value": "Average Final Rating Descending"}
                    ],
                    value="Average Final Rating Descending",
                    clearable=False,
                    style={"width": "290px", "fontSize": "16px", "cursor": "pointer"}
                )
            ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "justifyContent": "flex-end",
                    "margin": "10px 0px 20px 0",
                    "position": "absolute",
                    "right": "155px",
                }
            ),
        ],
            style={
                "display": "flex",
                "alignItems": "start",
                "padding": "20px",
                "gap": "1000px"
            }
        ),

        html.Div(
            id="ingredients-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "width": "1235px",
                "height": "auto",
                "gap": "20px",
                "padding": "20px",
                "position": "absolute",
                "top": "280px",
                "left": "510px"
            }
        ),

        html.Div(
            [
                html.Button("Previous", id="prev-page-button-ingredients", n_clicks=0),
                dcc.Input(
                    id="current-page-ingredients",
                    type="number",
                    value=1,
                    min=1,
                    style={"width": "50px", "margin": "0 10px"}
                ),
                html.Span(id="total-pages-ingredients", style={"marginRight": "10px"}),
                html.Button("Next", id="next-page-button-ingredients", n_clicks=0),
            ],
            style={"position": "absolute", "top": "230px", "left": "530px"},
        )
    ])

@cosmetic_app.callback(
    [
        Output("ingredients-grid", "children"),
        Output("total-pages-ingredients", "children"),
        Output("current-page-ingredients", "value")
    ],
    [
        Input("search-box-ingredients", "value"),
        Input("ingredient-filter-classification", "value"),
        Input("ingredient-filter-functions", "value"),
        Input("ingredient-filter-origin", "value"),
        Input("ingredients-sort", "value"),
        Input("current-page-ingredients", "value"),
        Input("prev-page-button-ingredients", "n_clicks"),
        Input("next-page-button-ingredients", "n_clicks"),
    ]
)
def update_ingredients_grid(search_value, classification_value, functions_value, origin_value, sort_value,
                            current_page, prev_clicks, next_clicks):

    _ = prev_clicks, next_clicks

    ingredients_data = []

    cosmetics_df = cosmetics_current_df.copy()

    for idx, ingredients_list in enumerate(cosmetics_df["Ingredients"]):
        if isinstance(ingredients_list, list):
            for ingredient in ingredients_list:
                if isinstance(ingredient, dict) and "Ingredient" in ingredient:
                    flattened_ingredient = {
                        "Ingredient": ingredient.get("Ingredient", ""),
                        "Classification": ", ".join(
                            ingredient.get("Details", {}).get("Classification", [])) or "Not available",
                        "Functions": ", ".join(
                            [f.split(":")[0].strip() for f in ingredient.get("Details", {}).get("Functions", [])]
                        ) or "Not available",
                        "Origin": ", ".join(ingredient.get("Details", {}).get("Origin", [])) or "Not available",
                        "Final rating": cosmetics_df.iloc[idx][
                            "Final rating"] if "Final rating" in cosmetics_df else None
                    }
                    ingredients_data.append(flattened_ingredient)

    ingredients_df = pd.DataFrame(ingredients_data)

    avg_ratings = ingredients_df.groupby("Ingredient")["Final rating"].mean().reset_index()
    avg_ratings.rename(columns={"Final rating": "Final rating average"}, inplace=True)

    ingredients_df = ingredients_df.merge(avg_ratings, on="Ingredient", how="left")
    ingredients_df = ingredients_df.drop_duplicates(subset=["Ingredient"], keep="first")

    if search_value:
        search_value = search_value.lower()
        ingredients_df = ingredients_df[
            ingredients_df["Ingredient"].str.lower().str.contains(search_value, na=False)
        ]

    if classification_value:
        ingredients_df = ingredients_df[
            ingredients_df["Classification"].apply(
                lambda classifications: any(c in classifications for c in classification_value)
            )
        ]

    if functions_value:
        ingredients_df = ingredients_df[
            ingredients_df["Functions"].apply(
                lambda functions: any(f in functions for f in functions_value)
            )
        ]

    if origin_value:
        ingredients_df = ingredients_df[
            ingredients_df["Origin"].apply(
                lambda origins: any(o in origins for o in origin_value)
            )
        ]

    if sort_value:
        if sort_value == "Average Final Rating Ascending":
            ingredients_df = ingredients_df.sort_values("Final rating average", ascending=True)
        elif sort_value == "Average Final Rating Descending":
            ingredients_df = ingredients_df.sort_values("Final rating average", ascending=False)

    items_per_page = 30
    total_items = len(ingredients_df)
    total_pages = max(1, -(-total_items // items_per_page))

    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "prev-page-button-ingredients" and current_page > 1:
        current_page -= 1
    elif triggered_id == "next-page-button-ingredients" and current_page < total_pages:
        current_page += 1

    start_index = (current_page - 1) * items_per_page
    end_index = start_index + items_per_page
    page_data = ingredients_df.iloc[start_index:end_index]

    cards = [
        html.Div([
            html.H3(row["Ingredient"], style={"fontSize": "18px", "marginBottom": "10px"}),
            html.P(f"Classification: {row['Classification']}"),
            html.P(f"Functions: {row['Functions']}"),
            html.P(f"Origin: {row['Origin']}"),
            html.P(f"Average Final Rating: {row['Final rating average']:.2f}")
        ], style={
            "border": "1px solid #ccc",
            "padding": "15px",
            "borderRadius": "5px",
            "margin": "0 0 10px 0",
            "backgroundColor": "#F5F2FB"
        })
        for _, row in page_data.iterrows()
    ]

    return cards, f"of {total_pages} pages", current_page

def cosmetic_details_screen(cosmetic_id):
    cosmetic = cosmetics_current_df[cosmetics_current_df["_id"] == cosmetic_id]
    historical_cosmetic = cosmetics_archived_df[cosmetics_archived_df["Name"] == cosmetic["Name"].iloc[0]]

    if cosmetic.empty:
        return html.Div("Cosmetic not found.", style={"fontSize": "20px", "color": "red"})

    if not historical_cosmetic.empty:
        historical_cosmetic = historical_cosmetic.iloc[0]

    cosmetic = cosmetic.iloc[0]

    similar_cosmetics = cosmetics_current_df[
        (cosmetics_current_df["Label"] == cosmetic["Label"]) & (cosmetics_current_df["_id"] != cosmetic["_id"])
        ]

    similar_cosmetics_sorted = similar_cosmetics.sort_values(by="Final rating", ascending=False)

    top_5_similar_cosmetics = similar_cosmetics_sorted.head(5)

    similar_cosmetics_elements = [
        html.Div(
            html.Div([
                dcc.Link(html.H4(cosmetic["Name"]), href=f"/cosmetic-details/{cosmetic['_id']}",
                         style={"color": "#212046"}),
                html.P(f"Final rating: {cosmetic['Final rating']}")
            ]),
            style={"marginBottom": "15px", "padding": "15px", "borderRadius": "5px", "backgroundColor": "#F6F3FB",
                   "boxShadow": "3px 3px 5px gray"
                   }
        )
        for _, cosmetic in top_5_similar_cosmetics.iterrows()
    ]

    return html.Div([
        dcc.Link(
            html.Button(
                "Go back to previous page",
                style={"padding": "10px", "fontSize": "16px", "borderRadius": "5px", "backgroundColor": "#e9e9ed",
                       "cursor": "pointer", "position": "absolute", "top": "60px", "left": "110px"}
            ),
            href="/cosmetics"
        ),

        html.Div([
            html.Div([
                html.H2(cosmetic["Name"]),
                html.P(f"Brand: {cosmetic['Brand']}"),
                html.P(f"Category: Face"),
                html.P(f"Subcategory: {cosmetic['Label']}"),
                html.P(f"Price: ${cosmetic['Price']}"),
                html.P(f"Skin Types: {', '.join(cosmetic['Skin']) if isinstance(cosmetic['Skin'], list) else 'N/A'}"),
                html.P(
                    f"Ingredients: {', '.join(ing.get('Ingredient', '') for ing in cosmetic['Ingredients'] if isinstance(ing, dict))}"),
                html.P(f"Current ratings:"),
                html.Div([
                    html.Div(
                        html.P(f"User:\n{cosmetic['User rating']}"),
                        style={"height": "100px", "width": "100px", "backgroundColor": "#F6F6F6", "padding": "10px",
                               "fontSize": "19px", "borderRadius": "5px", "display": "flex", "alignItems": "center",
                               "justifyContent": "center", "textAlign": "center", "boxShadow": "3px 3px 5px gray",
                               "whiteSpace": "pre-line"},
                    ),
                    html.Div(
                        html.P(f"Final:\n{cosmetic['Final rating']}"),
                        style={"height": "100px", "width": "100px", "backgroundColor": "#F6F3FB", "padding": "10px",
                               "fontSize": "19px", "borderRadius": "5px", "display": "flex", "alignItems": "center",
                               "justifyContent": "center", "textAlign": "center", "boxShadow": "3px 3px 5px gray",
                               "whiteSpace": "pre-line"},
                    ),
                    html.Div(
                        html.P(f"Ingredients:\n{cosmetic['Ingredients rating']}"),
                        style={"height": "100px", "width": "100px", "backgroundColor": "#F6F6F6", "padding": "10px",
                               "fontSize": "19px", "borderRadius": "5px", "display": "flex", "alignItems": "center",
                               "justifyContent": "center", "textAlign": "center", "boxShadow": "3px 3px 5px gray",
                               "whiteSpace": "pre-line"},
                    )
                ],
                    style={"display": "flex", "alignItems": "start", "gap": "20px", "justifyContent": "center"}
                ),
                html.P(f"Historical ratings:"),
                html.Div([
                    html.Div(
                        html.P(f"User:\n{historical_cosmetic['User rating']}"),
                        style={"height": "100px", "width": "100px", "backgroundColor": "#F6F6F6", "padding": "10px",
                               "fontSize": "19px", "borderRadius": "5px", "display": "flex", "alignItems": "center",
                               "justifyContent": "center", "textAlign": "center", "boxShadow": "3px 3px 5px gray",
                               "whiteSpace": "pre-line"},
                    ),
                    html.Div(
                        html.P(f"Final:\n{historical_cosmetic['Final rating']}"),
                        style={"height": "100px", "width": "100px", "backgroundColor": "#F6F3FB", "padding": "10px",
                               "fontSize": "19px", "borderRadius": "5px", "display": "flex", "alignItems": "center",
                               "justifyContent": "center", "textAlign": "center", "boxShadow": "3px 3px 5px gray",
                               "whiteSpace": "pre-line"},
                    ),
                    html.Div(
                        html.P(f"Ingredients:\n{historical_cosmetic['Ingredients rating']}"),
                        style={"height": "100px", "width": "100px", "backgroundColor": "#F6F6F6", "padding": "10px",
                               "fontSize": "19px", "borderRadius": "5px", "display": "flex", "alignItems": "center",
                               "justifyContent": "center", "textAlign": "center", "boxShadow": "3px 3px 5px gray",
                               "whiteSpace": "pre-line"},
                    )
                ],
                    style={"display": "flex", "alignItems": "start", "gap": "20px", "justifyContent": "center"}
                ),
            ],
                style={"fontSize": "19px"}
            )],
            style={
                "display": "flex",
                "flex-direction": "column",
                "alignItems": "center",
                "gap": "10px",
                "width": "600px",
                "padding": "10px 20px 20px 20px",
                "borderRadius": "8px",
                "boxShadow": "3px 3px 5px gray",
                "backgroundColor": "#DDDFF8",
                "position": "absolute",
                "left": "450px",
                "top": "30px"
            }
        ),
        html.Div([
            html.H2("Similar cosmetics:"),
            html.Div(
                id="similar-cosmetics",
                children=similar_cosmetics_elements
            )
        ],
            style={"position": "absolute", "left": "1200px", "top": "50px"}
        )
    ])

cosmetic_app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

@cosmetic_app.callback(
    Output("url", "pathname"),
    [Input("cosmetics-button", "n_clicks"),
     Input("ingredients-button", "n_clicks")],
    prevent_initial_call=True
)
def navigate(cosmetics_clicked, ingredients_clicked):
    if cosmetics_clicked:
        return "/cosmetics"
    elif ingredients_clicked:
        return "/ingredients"
    return dash.no_update

@cosmetic_app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_screen(pathname):
    if not pathname or pathname == "/":
        return cosmetics_screen()
    elif pathname == "/ingredients":
        return ingredients_screen()
    elif pathname == "/cosmetics":
        return cosmetics_screen()
    elif pathname.startswith("/cosmetic-details/"):
        cosmetic_id = pathname.split("/")[-1]
        return cosmetic_details_screen(cosmetic_id)
    return html.Div("404 Page Not Found", style={"fontSize": "24px", "color": "red"})

if __name__ == "__main__":
    cosmetic_app.run_server(debug=True)
