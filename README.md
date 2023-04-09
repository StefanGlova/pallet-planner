# pallet-planner

Pallet planner application is created as part of supply chain apps pack by Stefan Glova. This application contains two individual applications:
1. pallets planner
2. orders planner

1. pallet planner
This application takes as argument list of products and their qty which needs to be planned. Purpose is to plan, how products will be palletised. It uses
3 different sizes of boxes, smallest can be up to 20 on a pallet, medium up to 6 on a pallet and largest 1 box per pallet. Part of the application is 
database with all packing criteria (qty which fit for each product and each box). The application is mostly created in python, but algorithm is written in 
SQLite + python. Part of application is function called consolidate, which is optional, if required, it will combine qty of same products on delivery, if 
not, it will plan them all separately. The outcome is file with list of pallets and split of products into boxes on each pallet.

2. orders planner
This application takes as argument customer (it has set up individual target for each customer), list of back orders and list of current inventories. It accept
customer's SKU which are translated to supplier's SKU before calculation, then when order suggestion is created, it translates it back to customer's SKUs.
The outcome is list of products which customer needs to order to keep their targeted stock holding level.
