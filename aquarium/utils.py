from aquarium import AquariumAPI
import re
import json


# This is basically a mix-in - adds methods to AquariumAPI
class SampleHelper(AquariumAPI):
    def __init__(self, url, login, key, project=None):
        super(SampleHelper, self).__init__(url, login, key, project=project)

    def sample_type_id(self, type):
        # input string (e.g. "Fragment" returns its sample_type_id
        json_sample_type_id = self.find("sample_type", {"Name": type})

        return json_sample_type_id["rows"][0]["id"]

    def find_sample_substring(self, type, regex_str_tofind):
        # find based on a substring in name or description

        json_res = self.find("sample",
                             {"sample_type_id": self.sample_type_id(type)})
        samples = []
        pattern = re.compile(regex_str_tofind)
        for i in json_res["rows"]:
            name_matches = pattern.search(json.dumps(i["name"]))
            description_matches = pattern.search(json.dumps(i["description"]))
            if name_matches or description_matches:
                samples.append(i)

        return samples

    def find_primers(self, overhang_seq, anneal_seq):
        primers = []
        for i in self.find("sample",
                           {"sample_type_id": self.sample_type_id("Primer")}
                           )["rows"]:
            overhang_match = i["fields"]["Overhang Sequence"] == overhang_seq
            anneal_match = i["fields"]["Anneal Sequence"] == anneal_seq
            if overhang_match and anneal_match:
                primers.append(i)
        return primers
