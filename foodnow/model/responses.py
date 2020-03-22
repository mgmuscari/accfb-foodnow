

class Responses(object):
    @staticmethod
    def invalid_city_response():
        return {
            "actions": [
                {
                    "say": "I'm sorry, you are outside of the service area of Alameda County Community Food Bank"
                },
                {
                    "redirect": "task://goodbye"
                }
            ]
        }

    @staticmethod
    def valid_city_response(city):
        return {
            "actions": [
                {
                    "say": "I can help you find food near {}".format(city)
                },
                {
                    "redirect": "task://collect_address"
                }
            ]
        }

    @staticmethod
    def error_response():
        return {
            "actions": [
                {
                    "redirect": "task://error_condition"
                }
            ]
        }

    @staticmethod
    def found_pantry_response(name, address, city, formatted_address, geolocation):
        return {
            "actions": [
                {
                    "say": "I found {} at {} in {}".format(name, address, city)
                },
                {
                    "remember": {
                        "user_formatted_address": formatted_address,
                        "user_geo": geolocation,
                    }
                }
            ]
        }
