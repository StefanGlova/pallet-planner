import csv


def change_file(pp_codes_file, b_codes_file, proposal,
                branch_target, order):

    pp_code = []

    with open(pp_codes_file, "r") as file:
        line = csv.reader(file)
        # takes each PP product code from the file and add it to python list
        for product in line:
            if product[0][-1] == " ":
                product[0] = product[0][:-1]
            for item in product:
                product = item
                pp_code.append(product)

    b_code = []

    with open(b_codes_file, "r") as file:
        line = csv.reader(file)
        # takes each b product code from the file and add it to python list
        for product in line:
            for item in product:
                product = item
                b_code.append(product)

    full_list = []

    with open(proposal, "r") as file:
        lines = csv.reader(file)

        for product in lines:
            # print(product)
            # transfer b code from their current file to PP code for further use
            # PP codes and b codes are in the same sequences in two different
            # lists, so every index value of list matches up with each other
            a = pp_code.index(product[0])
            # print(a)
            product.append(b_code[a])
            # print(product)
            full_list.append(product)

    description = {}
    full_pack = {}

    with open(branch_target, "r") as file:
        line = csv.reader(file)
        for product in line:
            if product[0][-1] == " ":
                product[0] = product[0][:-1]
            description[product[0]] = product[3]
            full_pack[product[0]] = product[4]

    for product in full_list:
        # print(product[0])
        # print(description[product[0]])
        desc = description[product[0]]
        product.append(desc)

    for product in full_list:
        full_bag = full_pack[product[0]]
        if int(product[1]) % int(full_bag) != 0:
            product[1] = str((int(int(product[1]) / int(full_bag)) + 1) * int(full_bag))

    with open(order, "w") as file:
        # write header
        file.write("%s,%s,%s,%s\n" % ("SKU", "Buildbase SKU", "Description", "Quantity"))
        # using order list from the "to_order" function, write every product
        # and quantity to the new csv file
        for product in full_list:
            file.write("%s,%s,%s,%s\n" % (product[0], product[2], product[3], product[1]))
