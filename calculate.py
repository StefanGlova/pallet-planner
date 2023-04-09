import csv


def calculate(pp_codes_file, b_codes_file, back_orders_file, current_stock_file,
              branch_target, proposal):

    def pp_codes() -> list:
        """
        function open file with PP product codes sorted in sequence and transfers
        them to python list in the same sequence as b_codes() function does with
        b product codes
        :return: list of PP product codes
        """
        pp_code = []
        with open(pp_codes_file, "r") as file:
            line = csv.reader(file)
            # takes each PP product code from the file and add it to python list
            for product in line:
                for item in product:
                    product = item
                    pp_code.append(product)
        return pp_code

    def b_codes() -> list:
        """
        function open file with b product codes sorted in sequence and
        transfers them to python list in the same sequence as pp_codes() function
        does with PP product codes
        :return: list of b product codes
        """
        b_code = []
        with open(b_codes_file, "r") as file:
            line = csv.reader(file)
            # takes each b product code from the file and add it to python list
            for product in line:
                for item in product:
                    product = item
                    b_code.append(product)
        return b_code

    def net_qty() -> dict:
        """
        function calculates total net qty on back orders
        :return: dictionary with pairs of product and net back order quantity
        """
        # net_back_orders is dictionary with consolidated values of every product
        # on back orders
        net_back_orders = {}
        with open(back_orders_file, "r") as file:
            line = csv.reader(file)
            # read back orders file, line by line
            for product in line:
                # if product is in the file for the first time, add it to python
                # dictionary net_back_orders with quantity difference between total
                # on order minus quantity which is already delivered
                if product[0] not in net_back_orders:
                    qty = int(product[1]) - int(product[2])
                    net_back_orders[product[0]] = qty
                # if product is already in the python dictionary, find it, get its quantity
                # and add further quantity, which is difference between full ordered quantity
                # and already delivered quantity
                # certain product can appear on back order multiple times, so this else
                # condition keep executing every time
                else:
                    qty = int(net_back_orders.get(product[0])) + \
                          int(product[1]) - int(product[2])
                    net_back_orders[product[0]] = qty
        return net_back_orders

    def total_stock() -> dict:
        """
        function calculate total quantity on back orders
        + current available stock in branch
        :return: dictionary with pairs of product and total quantity
        """
        # total_s dictionary take all the info from net_back_orders and keep adding
        # products which are already available in b stock
        total_s = net
        not_in = []
        with open(current_stock_file, "r") as file:
            line = csv.reader(file)
            for product in line:
                # transfer b code from their current file to PP code for further use
                # PP codes and b codes are in the same sequences in two different
                # lists, so every index value of list matches up with each other
                index = B_code.index(product[0])
                product[0] = PP_code[index]
                # working with PP code going forward
                # these lines check if product is already in dictionary, for example
                # from back orders. If it is, then it just increase quantity by stock
                # available in the branch. If it is not, it will add new pair to the
                # dictionary
                if product[0] not in total_s:
                    total_s[product[0]] = product[1]
                else:
                    quantity = int(total_s.get(product[0])) + int(product[1])
                    total_s[product[0]] = quantity
        return total_s

    def to_order() -> dict:
        """
        function calculate total quantity which needs to be ordered
        to fulfil stock level target
        :return: dictionary with pairs of products and quantities
        """
        # new dictionary "order" is accumulating pairs of product and quantities
        # which needs to be ordered to meet requirement defined in database
        order = {}
        with open(branch_target, "r") as file:
            line = csv.reader(file)
            for product in line:
                # this statement is just fixing inaccuracy in database, as some
                # products have extra space after the code. If the space is there
                # it just removes it before further use
                if product[0][-1] == " ":
                    product[0] = product[0][:-1]
                # if product from database is neither on any back order, nor in branch
                # stock, this line of code add product to the "order"
                if product[0] not in total:
                    order[product[0]] = int(product[1])
                # if product is either on back order or in branch, this line checks if
                # it is under minimum safe stock quantity. If it is, it will add product
                # to the order with quantity to get to suggested safe stock. If product
                # is in stock, or in back order in required quantity, it will get executed
                elif int(product[2]) >= int(total.get(product[0])):
                    quantity = int(product[1]) - int(total.get(product[0]))
                    order[product[0]] = quantity
            return order

    def create_order() -> None:
        """
        function create new csv file with new order
        if file already exist with previous order, this function will delete old file
        and replace it with the new one
        :return: no return, just a new file
        """
        # this line creates a new empty file, or if file already exist, it will
        # open it and delete all content
        with open(proposal, "w") as file:
            # using order list from the "to_order" function, write every product
            # and quantity to the new csv file
            for key in new_order.keys():
                file.write("%s,%s\n" % (key, new_order[key]))
        return

    PP_code = pp_codes()
    B_code = b_codes()
    net = net_qty()
    total = total_stock()
    new_order = to_order()
    create_order()
