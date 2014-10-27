pdxcartscrape
=============

Overview
-------------
This package scrapes and normalizes information from [foodcartsportland.com](http://www.foodcartsportland.com/).

Usage
----
Running foodcarts.py will retrieve information from all carts, while cart_scrape.py retrieves info from individual cart pod pages (e.g. 12th and Hawthorne).

If invoked with `main()`, cart_scrape.py will yield .csv list(s) or .html page(s) with table, while `find_carts()` returns a list of FoodCart objects.

FoodCarts have 6 properties: `div`, the `<div>` HTML element that is parsed, `name`, `url`, `location`, `hours`, and `story`. Initialization requires passing a <div> (a la `find_carts(url)`). To populate other properties, `scrape_div()` must be run (for now?). If assigned to a variable, `scrape_div()` method returns a dict.

To do
-----
    + Finish accounting for all data variations
    + Implement export of location list
    + Make FoodCart attributes populate upon construction?
    + Implement database connectivity
    + Turn into webapp
