__author__ = 'idoivri'
import sys
import csv
import json
import ast
import requests


# def _bulk_geocode(addresses):
#     ret_dict = {}
#     url = 'http://maps.googleapis.com/maps/api/geocode/json'
#     for address in addresses:
#         # print 'fetching ' + address
#         res = requests.get(url, params={
#             'address': address,
#             'sensor': 'false'
#         })
#
#         # print(res.text)
#         #dictionary = json.load(res.json())
#
#         if res.status_code == 200:
#             data = json.loads(res.text)
#             print (data['results'][0]['geometry']['location'])
#             ret_dict[address] = data['results'][0]['geometry']['location']
#
#         else:
#             print ("ERROR: Requests returned status code {}".format(res.status_code))
#             ret_dict[address] = {}
#
#     return ret_dict

def _geocode(address):

    url = 'http://maps.googleapis.com/maps/api/geocode/json'

    # print 'fetching ' + address
    res = requests.get(url, params={
        'address': address,
        'sensor': 'false'
    })

    # print(res.text)

    if res.status_code == 200:
        data = json.loads(res.text)
        try:
            print (data['results'][0]['geometry']['location'])
            return data['results'][0]['geometry']['location']
        except IndexError:
            print ("ERROR: Requests returned no lat/lng for {}".format(address))
            return {'lat': None, 'lng': None}

    else:
        print ("ERROR: Requests returned status code {}".format(res.status_code))
        return {'lat': None, 'lng': None}

def _write_csv(businesses_list,target_file_name):
    with open(target_file_name, 'w') as f:

        try:
            writer = csv.writer(f)

            for row in businesses_list:
                writer.writerow(row)

        finally:
            f.close()

    return True


def _create_addresses_list(file_name,target_file_name):
    # read csv with file_name, create a list with addresses only, while appending city_name to it
    # print ("Reading from {}".format(file_name))
    # with open(file_name, newline='') as csvfile:
    # addresses_reader = csv.reader(csvfile, delimiter=',')
    # for row in addresses_reader:
    #         print(', '.join(row))

    csv_to_write = list()
    address_index = -1
    city_index = -1

    with open(file_name, newline='') as csvfile:
        address_reader = csv.reader(csvfile, lineterminator='\r\n')
        title_row = address_reader.__next__()
        print(title_row)
        address_index = title_row.index("address")
        city_index = title_row.index("city")

        #TODO: Assert indexes are not -1 !!!
        #print ("address index: {}, city index: {}".format(address_index, city_index))

        for row in address_reader:
            data_row = list()
            row_address = "{} {} {}".format(row[address_index], row[city_index], "ישראל")
            data_row.append(row_address)
            address_dict = _geocode(row_address)

            for i, data in enumerate(row):
                if i == address_index or i == city_index:
                    continue
                elif address_dict['lat'] == None or address_dict['lng'] == None:
                    print ("ERROR: no lng / lat for {} {}".format(row[4],row_address))
                elif title_row[i] == 'lat':
                    data_row.append(address_dict['lat'])
                elif title_row[i] == 'lng':
                    data_row.append(address_dict['lng'])
                else:
                    data_row.append(data)

            csv_to_write.append(data_row)

        _write_csv(csv_to_write,target_file_name)

if __name__ == '__main__':

    if len(sys.argv) <= 2:
        print("get_addresses.py : a command-line tool which creates lat/lng from addresses in a CSV file.")
        print("Assumes first line of CSV contains headers, and contains address and city in 2 different columns.")
        print("USAGE: get_addresses.py [CSV filename to read] [CSV filename to write to]")
        sys.exit(1)
    _create_addresses_list(sys.argv[1],sys.argv[2])