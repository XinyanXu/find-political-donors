#!/usr/bin/python
import numpy as np
import sys
import datetime


"""
Base class for Zip class and Data class
Zip class and Date class handle two output files grouped by zip/date 
independently from read input, check valid, to output
"""
class Base:
    def __init__(self, delimiter, input_file, output_file):
        self.delimiter = delimiter
        self.input_file = input_file
        self.output_file = output_file
        """
        data are stored in dictionary structure
        key: cmte_id, zip_code/transaction_dt
        value: count, total, [amount1, amount2, ...]
        """
        self.dict = {}

    def run(self):
        pass

    def reader(self):
        pass

    def writer(self):
        pass

    def insert(self, key, amount):
        """
        insert key and amount to dictionary
        :param key: cmte_id, zip_code/transaction_dt
        :param amount: transaction_amt
        :return:
        """
        value = self.dict.get(key)
        if not value:
            self.dict[key] = [0, 0, []]
        self.update(key, amount)

    def update(self, key, amount):
        """
        update count, total and append amount in the dictionary
        :param key: cmte_id, zip_code/transaction_dt
        :param amount: transaction_amt
        :return:
        """
        self.dict[key][0] += 1
        self.dict[key][1] += amount
        self.dict[key][2].append(amount)
        #average = int(round(total / count))


class Zip(Base):
    def __init__(self, delimiter, input_file, output_file):
        Base.__init__(self, delimiter, input_file, output_file)

    def run(self):
        self.reader()

    def reader(self):
        """
        reader funtion takes each record line by line from input file,
        insert it to dictionary
        and write each record to output file line by line in input order
        """
        output_file = open(self.output_file, 'w+')
        with open(self.input_file, 'r') as input_file:
            for line in input_file:
                values = line.strip().split('|')
                if not self.isValid(values):
                    continue
                cmte_id = values[0]
                zip_code = values[10][0:5]
                transaction_amt = int(values[14])
                key = (cmte_id, zip_code)
                self.insert(key, transaction_amt)
                self.writer(key, output_file)
        output_file.close()

    def writer(self, key, output_file):
        """
        writer funciton writes one record to output file in input order
        """
        count = self.dict.get(key)[0]
        total = self.dict.get(key)[1]
        median = int(round(np.median(self.dict.get(key)[2])))
        output_file.write(self.delimiter.join([key[0], key[1]] + map(str, [median, count, total])) + "\n")

    @staticmethod
    def isValid(values):
        """
        ignore the records if:
        0. input is not complete
        1. cmtd_id is invalid
        2. transaction_amt is invalid
        3. other_id is valid
        4. zip_code is empty/malformed
        :param values: raw input in array format
        :return: True/False
        """
        if len(values) < 21:
            return False
        cmte_id = values[0]
        zip_code = values[10]
        transaction_dt = values[13]
        transaction_amt = values[14]
        other_id = values[15]
        if other_id != '' or cmte_id == '' or transaction_amt == '' or len(zip_code) < 5 or not zip_code.isdigit():
            return False
        return True


class Date(Base):
    def __init__(self, delimiter, input_file, output_file):
        Base.__init__(self, delimiter, input_file, output_file)

    def run(self):
        self.reader()
        self.writer()

    def reader(self):
        """
        reader funtion takes each record line by line from input file,
        insert it to dictionary
        and write all records to output file at once in recipient lexical and then date chronological order
        """
        with open(self.input_file, 'r') as input_file:
            for line in input_file:
                values = line.strip().split('|')
                if not self.isValid(values):
                    continue
                cmte_id = values[0]
                transaction_dt = values[13]
                transaction_amt = int(values[14])
                key = (cmte_id, transaction_dt)
                self.insert(key, transaction_amt)

    def writer(self):
        """
        writer funciton writes all records to output file in recipient lexical and then date chronological order
        """
        with open(self.output_file, 'w+') as output_file:
            for key in sorted(self.dict.iterkeys()):
                count = self.dict.get(key)[0]
                total = self.dict.get(key)[1]
                median = int(round(np.median(self.dict.get(key)[2])))
                output_file.write(self.delimiter.join([key[0], key[1]] + map(str, [median, count, total])) + "\n")


    @staticmethod
    def isValid(values):
        """
        ignore the records if:
        0. input is not complete
        1. cmtd_id is invalid
        2. transaction_amt is invalid
        3. other_id is valid
        4. transaction_dt is empty/malformed
        :param values: raw input in array format
        :return: True/False
        """
        if len(values) < 21:
            return False
        cmte_id = values[0]
        zip_code = values[10]
        transaction_dt = values[13]
        transaction_amt = values[14]
        other_id = values[15]
        if other_id != '' or cmte_id == '' or transaction_amt == '':
            return False
        if len(transaction_dt) != 8:
            return False
        try :
            datetime.datetime(year=int(transaction_dt[4:]), month=int(transaction_dt[0:2]), day=int(transaction_dt[2:4]))
        except Exception:
            return False
        return True



def main():
    """
    check input command is valid
    """
    if len(sys.argv) < 4:
        raise ValueError("Syntax error: python find_political_donors.py input output1 output2")

    input_file = sys.argv[1]
    output_file_zip = sys.argv[2]
    output_file_date = sys.argv[3]

    date = Date("|", input_file, output_file_date)
    date.run()
    zip = Zip("|", input_file, output_file_zip)
    zip.run()


if __name__ == '__main__':
    try:
        main()
    except ValueError as err:
        print err
