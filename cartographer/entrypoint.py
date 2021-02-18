"""
Order your groceries automatically.
"""

from rich.console import Console

from cartographer import kroger, sheets, heuristics


def run():
    console = Console()

    console.rule("Cartographer")
    auth_session = kroger.authorize(console)

    with console.status("Setting up...") as status:
        status.update("Loading spreadsheet...")
        items = sheets.get_items(console)

        status.update("Loading model...")
        tokenizer, model = heuristics.load_tokenizer_and_model()
        console.log("Loaded model.")

        status.update("Picking groceries...")
        selected_items = {}

        for i, (item, count, description) in enumerate(items):
            status.update(f"Picking groceries [green]({i}/{len(items)})...")
            search_results = kroger.product_search(item, auth_session)
            selected = heuristics.select_item(
                item,
                search_results.json()["data"],
                description,
                tokenizer,
                model,
                console,
            )
            selected_items[selected["upc"]] = count

        status.update("Adding to cart...")
        kroger.add_to_cart(selected_items, auth_session)

    console.log("Done!")