import json
from typing import Any

import pytest
from typer.testing import CliRunner

from app.parse import amounts, class_list, convert, number, read_docs, recipe_key_name, slugify

Json = dict[str, Any]


def ref(class_name: str) -> str:
    base = class_name.removesuffix("_C")
    return f"/Script/Engine.BlueprintGeneratedClass'/Game/FactoryGame/{base}.{class_name}'"


def entries(*pairs: tuple[str, float]) -> str:
    return "(" + ",".join(f'(ItemClass="{ref(c)}",Amount={a})' for c, a in pairs) + ")"


def buildings(*classes: str) -> str:
    return "(" + ",".join(f'"/Game/FactoryGame/Buildable/{c}.{c}"' for c in classes) + ")"


def group(native_class: str, classes: list[Json]) -> Json:
    return {"NativeClass": f"/Script/CoreUObject.Class'/Script/FactoryGame.{native_class}'", "Classes": classes}


def item(class_name: str, name: str, form: str = "RF_SOLID", stack: str = "SS_BIG") -> Json:
    return {"ClassName": class_name, "mDisplayName": name, "mForm": form, "mStackSize": stack}


def recipe(
    class_name: str, name: str, ingredients: str, products: str, produced_in: str, time: str = "2.000000", events: str = ""
) -> Json:
    return {
        "ClassName": class_name,
        "mDisplayName": name,
        "mIngredients": ingredients,
        "mProduct": products,
        "mManufactoringDuration": time,
        "mProducedIn": produced_in,
        "mRelevantEvents": events,
    }


@pytest.fixture
def docs() -> list[Json]:
    """Minimal game Docs file, in the same shape as CommunityResources/Docs/en-US.json."""
    return [
        group(
            "FGResourceDescriptor",
            [
                item("Desc_OreIron_C", "Iron Ore", stack="SS_MEDIUM"),
                item("Desc_LiquidOil_C", "Crude Oil", form="RF_LIQUID", stack="SS_FLUID"),
            ],
        ),
        group(
            "FGItemDescriptor",
            [
                item("Desc_IronIngot_C", "Iron Ingot", stack="SS_MEDIUM"),
                item("Desc_Plastic_C", "Plastic"),
                item("Desc_HeavyOilResidue_C", "Heavy Oil Residue", form="RF_LIQUID", stack="SS_FLUID"),
                item("Desc_Gift_C", "FICSMAS Gift", stack="SS_HUGE"),
                item("Desc_Unused_C", "Unused Part"),
            ],
        ),
        group(
            "FGBuildableManufacturer",
            [
                {"ClassName": "Build_SmelterMk1_C", "mDisplayName": "Smelter", "mPowerConsumption": "4.000000"},
                {"ClassName": "Build_OilRefinery_C", "mDisplayName": "Refinery", "mPowerConsumption": "30.000000"},
            ],
        ),
        group(
            "FGBuildableManufacturerVariablePower",
            [{"ClassName": "Build_Converter_C", "mDisplayName": "Converter", "mPowerConsumption": "0.100000"}],
        ),
        group(
            "FGRecipe",
            [
                recipe(
                    "Recipe_IngotIron_C",
                    "Iron Ingot",
                    entries(("Desc_OreIron_C", 1)),
                    entries(("Desc_IronIngot_C", 1)),
                    buildings("Build_SmelterMk1_C", "BP_WorkBenchComponent_C"),
                ),
                recipe(
                    "Recipe_Plastic_C",
                    "Plastic",
                    entries(("Desc_LiquidOil_C", 3000)),
                    entries(("Desc_Plastic_C", 2), ("Desc_HeavyOilResidue_C", 1000)),
                    buildings("Build_OilRefinery_C"),
                    time="6.000000",
                ),
                recipe(
                    "Recipe_Alternate_PureIronIngot_C",
                    "Alternate: Pure Iron Ingot",
                    entries(("Desc_OreIron_C", 7)),
                    entries(("Desc_IronIngot_C", 13)),
                    buildings("Build_SmelterMk1_C"),
                    time="12.000000",
                ),
                recipe(
                    "Recipe_Gift_C",
                    "FICSMAS Gift",
                    entries(("Desc_OreIron_C", 1)),
                    entries(("Desc_Gift_C", 1)),
                    buildings("Build_SmelterMk1_C"),
                    events="(EV_Christmas)",
                ),
                recipe(
                    "Recipe_Unused_C",
                    "Unused Part",
                    entries(("Desc_IronIngot_C", 1)),
                    entries(("Desc_Unused_C", 1)),
                    buildings("BP_WorkBenchComponent_C"),
                ),
            ],
        ),
        group(
            "FGSchematic",
            [
                {
                    "mType": "EST_Milestone",
                    "mTechTier": "5",
                    "mUnlocks": [{"mRecipes": f'("{ref("Recipe_Plastic_C")}")'}],
                },
                {
                    "mType": "EST_Tutorial",
                    "mTechTier": "0",
                    "mUnlocks": [{"mRecipes": f'("{ref("Recipe_IngotIron_C")}")'}],
                },
                {
                    "mType": "EST_ResourceSink",
                    "mTechTier": "0",
                    "mUnlocks": [{"mRecipes": f'("{ref("Recipe_Plastic_C")}")'}],
                },
            ],
        ),
        group(
            "FGBuildableResourceExtractor",
            [
                {
                    "ClassName": "Build_MinerMk1_C",
                    "mDisplayName": "Miner Mk.1",
                    "mAllowedResourceForms": "(RF_SOLID)",
                    "mItemsPerCycle": "1",
                    "mExtractCycleTime": "1.000000",
                    "mPowerConsumption": "5.000000",
                },
                {
                    "ClassName": "Build_OilPump_C",
                    "mDisplayName": "Oil Extractor",
                    "mAllowedResourceForms": "(RF_LIQUID)",
                    "mItemsPerCycle": "2000",
                    "mExtractCycleTime": "1.000000",
                    "mPowerConsumption": "40.000000",
                },
            ],
        ),
        group(
            "FGBuildableConveyorBelt",
            [
                {"mDisplayName": "Conveyor Belt Mk.2", "mSpeed": "240.000000"},
                {"mDisplayName": "Conveyor Belt Mk.1", "mSpeed": "120.000000"},
            ],
        ),
        group(
            "FGBuildablePipeline",
            [
                {"mDisplayName": "Pipeline Mk.1", "mFlowLimit": "5.000000"},
                {"mDisplayName": "Clean Pipeline Mk.1", "mFlowLimit": "5.000000"},
            ],
        ),
    ]


def by_key(entries: list[Json]) -> dict[str, Json]:
    return {e["key_name"]: e for e in entries}


class TestHelpers:
    def test_slugify(self):
        assert slugify("Iron Plate") == "iron-plate"
        assert slugify("Miner Mk.1") == "miner-mk-1"

    def test_recipe_key_name(self):
        assert recipe_key_name("Screws") == "screws"
        assert recipe_key_name("Alternate: Cast Screws") == "alt-cast-screws"

    def test_number(self):
        assert number("2.000000") == 2 and isinstance(number("2.000000"), int)
        assert number("2.5") == 2.5

    def test_class_list(self):
        assert class_list(buildings("Build_SmelterMk1_C", "Build_FoundryMk1_C")) == ["Build_SmelterMk1_C", "Build_FoundryMk1_C"]

    def test_amounts(self):
        assert amounts(entries(("Desc_IronPlate_C", 6), ("Desc_Water_C", 1500.5))) == [
            ("Desc_IronPlate_C", 6.0),
            ("Desc_Water_C", 1500.5),
        ]


class TestReadDocs:
    @pytest.mark.parametrize("encoding", ["utf-16", "utf-8-sig", "utf-8"])
    def test_should_read_every_encoding(self, tmp_path, docs, encoding):
        file = tmp_path / "en-US.json"
        file.write_text(json.dumps(docs), encoding=encoding)
        assert read_docs(file) == docs


class TestConvert:
    def test_should_keep_only_production_recipes_outside_events(self, docs):
        recipes = by_key(convert(docs)["recipes"])
        assert set(recipes) == {"iron-ingot", "plastic", "alt-pure-iron-ingot"}

    def test_should_list_standard_recipes_before_alternates(self, docs):
        assert [r["key_name"] for r in convert(docs)["recipes"]] == ["iron-ingot", "plastic", "alt-pure-iron-ingot"]

    def test_should_convert_recipe(self, docs):
        assert by_key(convert(docs)["recipes"])["iron-ingot"] == {
            "name": "Iron Ingot",
            "key_name": "iron-ingot",
            "category": "smelting1",
            "time": 2,
            "ingredients": [["iron-ore", 1]],
            "products": [["iron-ingot", 1]],
        }

    def test_should_convert_fluid_amounts_to_cubic_meters(self, docs):
        plastic = by_key(convert(docs)["recipes"])["plastic"]
        assert plastic["category"] == "refining"
        assert plastic["ingredients"] == [["crude-oil", 3]]
        assert plastic["products"] == [["plastic", 2], ["heavy-oil-residue", 1]]

    def test_should_split_items_and_fluids(self, docs):
        data = convert(docs)
        assert set(by_key(data["items"])) == {"iron-ore", "iron-ingot", "plastic"}
        assert set(by_key(data["fluids"])) == {"crude-oil", "heavy-oil-residue"}
        assert by_key(data["items"])["iron-ore"]["stack_size"] == 100

    def test_should_compute_tiers_from_progression(self, docs):
        data = convert(docs)
        items, fluids = by_key(data["items"]), by_key(data["fluids"])
        assert items["iron-ore"]["tier"] == -1
        assert items["iron-ingot"]["tier"] == 0
        assert items["plastic"]["tier"] == 5  # the resource sink unlock at tier 0 is ignored
        assert fluids["heavy-oil-residue"]["tier"] == 5

    def test_should_list_resources(self, docs):
        assert convert(docs)["resources"] == [
            {"key_name": "crude-oil", "category": "fluid"},
            {"key_name": "iron-ore", "category": "mineral"},
        ]

    def test_should_list_buildings_used_by_recipes(self, docs):
        assert convert(docs)["buildings"] == [
            {"name": "Refinery", "key_name": "refinery", "category": "refining", "power": 30},
            {"name": "Smelter", "key_name": "smelter", "category": "smelting1", "power": 4},
        ]

    def test_should_compute_extraction_rates(self, docs):
        miners = by_key(convert(docs)["miners"])
        assert miners["miner-mk-1"]["base_rate"] == 60
        assert miners["oil-extractor"] == {
            "name": "Oil Extractor",
            "key_name": "oil-extractor",
            "category": "fluid",
            "base_rate": 120,
            "power": 40,
        }

    def test_should_convert_belts_and_pipes(self, docs):
        data = convert(docs)
        assert [(b["key_name"], b["name"], b["rate"]) for b in data["belts"]] == [
            ("belt1", "Conveyor Belt Mk.1", 60),
            ("belt2", "Conveyor Belt Mk.2", 120),
        ]
        assert data["pipes"] == [{"name": "Pipeline Mk.1", "key_name": "pipe1", "rate": 300}]

    def test_should_disambiguate_recipes_sharing_a_name(self, docs):
        recipes = next(g for g in docs if g["NativeClass"].endswith("FGRecipe'"))["Classes"]
        recipes.append(
            recipe(
                "Recipe_IngotIron_Refinery_C",
                "Iron Ingot",
                entries(("Desc_OreIron_C", 1)),
                entries(("Desc_IronIngot_C", 1)),
                buildings("Build_OilRefinery_C"),
            )
        )
        keys = [r["key_name"] for r in convert(docs)["recipes"]]
        assert "iron-ingot" in keys and "iron-ingot-refining" in keys


class TestParseCommand:
    def test_should_write_the_data_file(self, tmp_path, docs):
        import satis

        source = tmp_path / "en-US.json"
        source.write_text(json.dumps(docs), encoding="utf-16")
        output = tmp_path / "data.json"

        result = CliRunner().invoke(satis.app, ["parse", "--file", str(source), "--output", str(output)])

        assert result.exit_code == 0, result.output
        assert json.loads(output.read_text()) == convert(docs)

    def test_should_fail_on_missing_file(self, tmp_path):
        import satis

        result = CliRunner().invoke(satis.app, ["parse", "--file", str(tmp_path / "missing.json")])
        assert result.exit_code == 2
