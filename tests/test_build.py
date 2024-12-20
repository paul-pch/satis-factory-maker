# import pytest
# from typer.testing import CliRunner

# from app.build import app, get_recipes_for_item, check_ingredients


# runner = CliRunner()


# def test_should_handle_existing_item():
#     # Test that the app command handles an existing item correctly
#     result = runner.invoke(
#         app, ["item", "--query", "existing_item", "--minute-rate", "1"]
#     )
#     assert result.exit_code == 0
#     assert "Matching recipes" in result.output


# def test_should_handle_nonexistent_item():
#     # Test that the app command handles a nonexistent item correctly
#     result = runner.invoke(
#         app, ["item", "--query", "nonexistent_item", "--minute-rate", "1"]
#     )
#     assert result.exit_code == 1
#     assert "Item 'nonexistent_item' not found." in result.output


# def test_should_return_recipes_for_existing_item():
#     # Test that the get_recipes_for_item function returns recipes for an existing item
#     recipes = [{"products": [("existing_item", 1)]}]
#     assert get_recipes_for_item(recipes, "existing_item") == recipes


# def test_should_raise_error_for_nonexistent_item():
#     # Test that the get_recipes_for_item function raises an error for a nonexistent item
#     recipes = [{"products": [("existing_item", 1)]}]
#     with pytest.raises(SystemExit):
#         get_recipes_for_item(recipes, "nonexistent_item")


# def test_should_not_return_complex_ingredients():
#     # Test that the check_ingredients function does not return complex ingredients when they do not exist
#     recipe = {"ingredients": [("resource1", 1), ("fluid1", 2)]}
#     resources = [{"key_name": "resource1"}]
#     fluids = [{"key_name": "fluid1"}]
#     assert check_ingredients(recipe, resources, fluids) == []


# def test_should_return_complex_ingredients():
#     # Test that the check_ingredients function returns complex ingredients when they exist
#     recipe = {"ingredients": [("resource1", 1), ("complex1", 2)]}
#     resources = [{"key_name": "resource1"}]
#     fluids = []
#     assert check_ingredients(recipe, resources, fluids) == ["complex1"]
