#!/usr/bin/python3

import json
import re
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

console = Console()

Json = dict[str, Any]

STACK_SIZES = {"SS_ONE": 1, "SS_SMALL": 50, "SS_MEDIUM": 100, "SS_BIG": 200, "SS_HUGE": 500, "SS_FLUID": 50000}

MANUFACTURERS = ("FGBuildableManufacturer", "FGBuildableManufacturerVariablePower")
EXTRACTORS = ("FGBuildableResourceExtractor", "FGBuildableFrackingExtractor")

# Recipe categories used by the build/search commands, one per production building
CATEGORIES = {
    "Constructor": "crafting1",
    "Assembler": "crafting2",
    "Manufacturer": "crafting3",
    "Smelter": "smelting1",
    "Foundry": "smelting2",
    "Refinery": "refining",
    "Packager": "packaging",
    "Blender": "blending",
    "Particle Accelerator": "accelerating",
    "Converter": "converting",
    "Quantum Encoder": "encoding",
}

# Schematics that do not represent progression (shop, cosmetics, scripted events)
IGNORED_SCHEMATICS = ("EST_ResourceSink", "EST_Customization", "EST_Custom")


def parse(
    file: Annotated[Path, typer.Option(help="Game Docs file (CommunityResources/Docs/en-US.json)", exists=True, dir_okay=False)],
    output: Annotated[Path, typer.Option(help="Simplified data file to write")] = Path("data/data.json"),
):
    """
    Parse the game Docs file into the simplified data file used by the other commands.
    """
    data = convert(read_docs(file))

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    counts = ", ".join(f"{len(v)} {k}" for k, v in data.items())
    console.print(f"[green]{output} written: {counts}[/green]")


def read_docs(file: Path) -> list[Json]:
    # The game ships the file in UTF-16, copies are often re-encoded in UTF-8
    raw = file.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    return json.loads(raw.decode(encoding))


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def recipe_key_name(name: str) -> str:
    if name.startswith("Alternate: "):
        return "alt-" + slugify(name.removeprefix("Alternate: "))
    return slugify(name)


def number(value: str | float) -> int | float:
    value = float(value)
    return int(value) if value.is_integer() else value


def class_name(path: str) -> str:
    # ".../Desc_IronPlate.Desc_IronPlate_C'" -> "Desc_IronPlate_C"
    return path.rsplit(".", 1)[-1].strip("'\"")


def class_list(raw: str) -> list[str]:
    # '("/Game/.../A.A_C","/Game/.../B.B_C")' -> ["A_C", "B_C"]
    return [class_name(p) for p in re.findall(r'"([^"]+)"', raw)]


def amounts(raw: str) -> list[tuple[str, float]]:
    # '((ItemClass="...Desc_X_C\'",Amount=6),...)' -> [("Desc_X_C", 6.0), ...]
    return [(class_name(m[0]), float(m[1])) for m in re.findall(r'ItemClass="([^"]+)",Amount=([\d.]+)', raw)]


def convert(docs: list[Json]) -> Json:
    """
    Convert the game Docs (classes grouped by native class) into the simplified format keyed by key_name.
    """
    native: dict[str, list[Json]] = {group["NativeClass"].split(".")[-1].rstrip("'"): group["Classes"] for group in docs}

    # Every class with a form and a stack size is an item (parts, resources, fluids, biomass, ...)
    source_items: dict[str, Json] = {
        c["ClassName"]: c for classes in native.values() for c in classes if "mForm" in c and "mStackSize" in c
    }
    resource_classes = {c["ClassName"] for c in native["FGResourceDescriptor"]}
    manufacturers = {c["ClassName"]: c for nc in MANUFACTURERS for c in native.get(nc, [])}

    def is_liquid(item_class: str) -> bool:
        return source_items[item_class]["mForm"] in ("RF_LIQUID", "RF_GAS")

    def key(item_class: str) -> str:
        return slugify(source_items[item_class]["mDisplayName"])

    def quantity(item_class: str, amount: float) -> int | float:
        # Fluid amounts are in liters in the game files
        return number(amount / 1000 if is_liquid(item_class) else amount)

    # Keep recipes made in a production building, outside of seasonal events
    machine_recipes: list[Json] = []
    for c in native["FGRecipe"]:
        produced_in = [b for b in class_list(c["mProducedIn"]) if b in manufacturers]
        if produced_in and not c["mRelevantEvents"]:
            machine_recipes.append(
                {
                    "className": c["ClassName"],
                    "name": c["mDisplayName"],
                    "building": manufacturers[produced_in[0]]["mDisplayName"],
                    "time": c["mManufactoringDuration"],
                    "ingredients": amounts(c["mIngredients"]),
                    "products": amounts(c["mProduct"]),
                }
            )

    # Lowest progression tier unlocking a recipe that produces the item
    recipe_tier: dict[str, int] = {}
    for schematic in native["FGSchematic"]:
        if schematic["mType"] in IGNORED_SCHEMATICS:
            continue
        tier = int(schematic["mTechTier"])
        for unlock in schematic["mUnlocks"]:
            for recipe_class in class_list(unlock.get("mRecipes", "")):
                recipe_tier[recipe_class] = min(recipe_tier.get(recipe_class, tier), tier)
    item_tier: dict[str, int] = {item_class: -1 for item_class in resource_classes}
    for recipe in machine_recipes:
        tier = recipe_tier.get(recipe["className"])
        if tier is None:
            continue
        for product, _ in recipe["products"]:
            item_tier[product] = min(item_tier.get(product, tier), tier)

    used_items = resource_classes | {
        item_class for recipe in machine_recipes for item_class, _ in recipe["ingredients"] + recipe["products"]
    }
    items: list[Json] = []
    fluids: list[Json] = []
    for item_class in sorted(used_items, key=key):
        if is_liquid(item_class):
            fluids.append(
                {"name": source_items[item_class]["mDisplayName"], "key_name": key(item_class), "tier": item_tier.get(item_class)}
            )
        else:
            items.append(
                {
                    "name": source_items[item_class]["mDisplayName"],
                    "key_name": key(item_class),
                    "tier": item_tier.get(item_class),
                    "stack_size": STACK_SIZES.get(source_items[item_class]["mStackSize"]),
                }
            )

    resources = [
        {"key_name": key(item_class), "category": "fluid" if is_liquid(item_class) else "mineral"}
        for item_class in sorted(resource_classes, key=key)
    ]

    # Standard recipes first so that the default choice is the base recipe
    recipes: list[Json] = []
    for recipe in sorted(machine_recipes, key=lambda r: (r["name"].startswith("Alternate: "), r["name"])):
        category = CATEGORIES[recipe["building"]]
        key_name = recipe_key_name(recipe["name"])
        # Some recipes share a name across buildings (e.g. Turbo Rifle Ammo)
        if any(r["key_name"] == key_name for r in recipes):
            key_name = f"{key_name}-{category}"
        recipes.append(
            {
                "name": recipe["name"],
                "key_name": key_name,
                "category": category,
                "time": number(recipe["time"]),
                "ingredients": [[key(i), quantity(i, amount)] for i, amount in recipe["ingredients"]],
                "products": [[key(p), quantity(p, amount)] for p, amount in recipe["products"]],
            }
        )

    used_buildings = {recipe["building"] for recipe in machine_recipes}
    buildings = [
        {
            "name": c["mDisplayName"],
            "key_name": slugify(c["mDisplayName"]),
            "category": CATEGORIES[c["mDisplayName"]],
            "power": number(c["mPowerConsumption"]),
        }
        for c in sorted(manufacturers.values(), key=lambda c: c["mDisplayName"])
        if c["mDisplayName"] in used_buildings
    ]

    miners: list[Json] = []
    for c in sorted((c for nc in EXTRACTORS for c in native.get(nc, [])), key=lambda c: c["mDisplayName"]):
        liquid = "RF_LIQUID" in c["mAllowedResourceForms"]
        rate = float(c["mItemsPerCycle"]) / float(c["mExtractCycleTime"]) * 60
        miners.append(
            {
                "name": c["mDisplayName"],
                "key_name": slugify(c["mDisplayName"]),
                "category": "fluid" if liquid else "mineral",
                "base_rate": number(rate / 1000 if liquid else rate),
                "power": number(c["mPowerConsumption"]),
            }
        )

    # Belt speed is in half items per minute, pipe flow in m³ per second
    belts = [
        {"name": c["mDisplayName"], "key_name": f"belt{i}", "rate": number(float(c["mSpeed"]) / 2)}
        for i, c in enumerate(sorted(native["FGBuildableConveyorBelt"], key=lambda c: float(c["mSpeed"])), start=1)
    ]
    pipes = [
        {"name": c["mDisplayName"], "key_name": f"pipe{i}", "rate": number(float(c["mFlowLimit"]) * 60)}
        for i, c in enumerate(
            sorted(
                (c for c in native["FGBuildablePipeline"] if not c["mDisplayName"].startswith("Clean ")),
                key=lambda c: float(c["mFlowLimit"]),
            ),
            start=1,
        )
    ]

    return {
        "belts": belts,
        "pipes": pipes,
        "buildings": buildings,
        "miners": miners,
        "items": items,
        "fluids": fluids,
        "recipes": recipes,
        "resources": resources,
    }
