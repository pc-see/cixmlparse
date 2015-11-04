#!/usr/bin/env python
import os
import xmltodict
from tabulate import tabulate

class AbstractLogsParser(object):
    # Different test statuses
    TEST_RES_PASS = 0
    TEST_RES_FAIL = 1
    TEST_RES_SKIP = 2

    def __init__(self, logs_extension, root_dir):
        """
        Base class constructor
        @param  logs_extension  extension of log parse to parse
        @param  root_dir        path to root directory
        """
        self._logs_ext = "." + logs_extension
        self.process_logs(root_dir)
        self.generate_detailed_report()

    def get_result_by_type(self, tc_result):
        """
        Returns number of passed, failed or skipped tests
        @param  result_type     type of results to return
        """
        status = tc_result["@result"]
        if status == "PASS":
            return self.TEST_RES_PASS
        if status == "FAIL":
            return self.TEST_RES_FAIL
        if status == "SKIP":
            return self.TEST_RES_SKIP
        return -1

    def calc_success_rate(self, result_stats):
        """
        Calculate success rate of test
        @param  result_stats    statistic of test result
        """
        return result_stats["PASS"] * 1.0 / (result_stats["PASS"] + \
               result_stats["FAIL"])

    def generate_detailed_report(self):
        """
        Generate detailed report on each test suite
        """
        try:
            f = open("./report.txt","w")
            # report test stats summary
            status_types = ["PASS", "FAIL", "SKIP"]
            result_stats = dict(zip(status_types, [0, 0, 0]))
            for foo in self.test_results:
                for bar in foo["test_results"]["tc_result"]:
                    status = self.get_result_by_type(bar)
                    if status == 0:
                        result_stats["PASS"] += 1
                    if status == 1:
                        result_stats["FAIL"] += 1
                    if status == 2:
                        result_stats["SKIP"] += 1
            success_rate = round(self.calc_success_rate(result_stats), 2)
            result_stats.update(SUCCESSRATE=success_rate)
            headers = status_types + ["SUCCESSRATE"]
            data = [(result_stats[foo] for foo in headers)]
            data_table = tabulate(data, headers=headers, tablefmt="simple")
            f.write("[ SUMMARY ]\n\n%s" % data_table)
            # report test stats for every tests
            headers = ["NAME", "ENV", "DEBUG"] + status_types + ["SUCCESSRATE"]
            data = []
            for foo in self.test_results:
                row = [foo["test_results"][bar] for bar in
                      ["@test_suite", "environment"]]
                if "debug" in foo["test_results"].keys():
                    row.append(foo["test_results"]["debug"])
                else:
                    row.append("-")
                result_stats = dict(zip(status_types, [0, 0, 0]))
                for bar in foo["test_results"]["tc_result"]:
                    status = self.get_result_by_type(bar)
                    if status == 0:
                        result_stats["PASS"] += 1
                    if status == 1:
                        result_stats["FAIL"] += 1
                    if status == 2:
                        result_stats["SKIP"] += 1
                success_rate = round(self.calc_success_rate(result_stats), 2)
                result_stats.update(SUCCESSRATE=success_rate)
                row.extend([result_stats[qux] for qux in
                           status_types + ["SUCCESSRATE"]])
                data.append(row)
            data_table = tabulate(data, headers=headers, tablefmt="simple")
            f.write("\n\n[ TEST RESULTS ]\n\n%s" % data_table)
            # report test stats for each tests suit
            f.write("\n\n[ DETAILED TEST RESULTS ]\n\n")
            for foo in self.test_results:
                test_name = foo["test_results"]["@test_suite"]
                headers = ["ID", "RESULT", "DEBUG", "REASON"]
                data = []
                for bar in foo["test_results"]["tc_result"]:
                    row = [bar[qux] for qux in ["@id", "@result"]]
                    if "debug" in bar.keys():
                        row.append(bar["debug"])
                    else:
                        row.append("-")
                    if "reason" in bar.keys():
                        row.append(bar["reason"])
                    else:
                        row.append("-")
                    data.append(row)
                data_table = tabulate(data, headers=headers, tablefmt="simple")
                f.write("%s\n\n%s\n\n" % (test_name, data_table))
            f.close()
        except:
            raise Exception("generate_detailed_report is not implemented")

    def process_logs(self, root_dir):
        """
        Parses all log files with target extension in the specified folder
        @param  root_dir        root folder to look up for log files
        """
        try:
            if "~" in root_dir:
                root_dir = root_dir.replace("~", os.path.expanduser("~"))
            test_results = []
            for root, dir_names, file_names in os.walk(root_dir):
                for file_name in file_names:
                    if self._logs_ext in file_name:
                        xml_path = os.path.join(root, file_name)
                        test_result = xmltodict.parse(
                                      open(xml_path, "rb").read())
                        test_results.append(test_result)
            self.test_results = test_results
        except:
            raise Exception("process_logs is not implemented")
