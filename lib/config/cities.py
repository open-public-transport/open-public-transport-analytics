#
# Main
#

class Cities:

    cities = [
        {"name": "berlin", "query": "Berlin, Germany", "area": 891, "inhabitants": 3_600_000,
         "bounding_box": [13.088333218007715, 52.33824183586156, 13.759587218876971, 52.67491714954712],
         "transport_association": "vbb"},
        {"name": "bochum", "query": "Bochum, Germany", "area": 145, "inhabitants": 364_000,
         "bounding_box": [7.102082282000026, 51.41051770900003, 7.349335097000051, 51.531372340000075],
         "transport_association": "vrr"},
        {"name": "bonn", "query": "Bonn, Germany", "area": 141, "inhabitants": 330_000,
         "bounding_box": [7.022537442000043, 50.63268994200007, 7.210679743000071, 50.77437020800005],
         "transport_association": "vrs"},
        # {"name": "bremen", "query": "Bremen, Germany", "area": 318, "inhabitants": 566_000,
        # "bounding_box": [8.481735118728654, 53.01102137832358, 8.990780355986436, 53.60761767768827],
        # "transport_association": None },
        {"name": "cottbus", "query": "Cottbus, Germany", "area": 165, "inhabitants": 89_000,
         "bounding_box": [14.273306525769822, 51.69248183636231, 14.501295507607326, 51.86416174658669],
         "transport_association": "vbb"},
        {"name": "dortmund", "query": "Dortmund, Germany", "area": 280, "inhabitants": 597_000,
         "bounding_box": [7.303593755474529, 51.416072806289165, 7.637115868651861, 51.59952017917111],
         "transport_association": "vrr"},
        {"name": "dresden", "query": "Dresden, Germany", "area": 328, "inhabitants": 556_000,
         "bounding_box": [13.579721093821485, 50.9752258280855, 13.965849226642415, 51.176915429975296],
         "transport_association": "vms"},
        {"name": "duesseldorf", "query": "Düsseldorf, Germany", "area": 217, "inhabitants": 620_000,
         "bounding_box": [6.68881312000002, 51.124375875000055, 6.939933901000074, 51.352486457000055],
         "transport_association": "vrr"},
        {"name": "duisburg", "query": "Duisburg, Germany", "area": 232, "inhabitants": 495_000,
         "bounding_box": [6.625616443645652, 51.333198590659165, 6.83045999817622, 51.560220016593334],
         "transport_association": "vrr"},
        # {"name": "frankfurt-main", "query": "Frankfurt (Main), Germany", "area": 248, "inhabitants": 764_000,
        # "bounding_box": [8.47276067000007, 50.01524884200006, 8.800381926000057, 50.22712951500006],
        # "transport_association": None},
        {"name": "frankfurt-oder", "query": "Frankfurt (Oder), Germany", "area": 147, "inhabitants": 57_000,
         "bounding_box": [14.394834417176915, 52.25277200883128, 14.600891619659311, 52.39823335093446],
         "transport_association": "vbb"},
        {"name": "hamburg", "query": "Hamburg, Germany", "area": 755, "inhabitants": 1_851_000,
         "bounding_box": [9.73031519588174, 53.39507758854026, 10.325959157503767, 53.73808674380358],
         "transport_association": "hvv"},
        {"name": "hamm", "query": "Hamm, Germany", "area": 226, "inhabitants": 178_000,
         "bounding_box": [7.675536280292723, 51.57805231922079, 7.997528913639968, 51.744766475157476],
         "transport_association": "vrr"},
        {"name": "koeln", "query": "Köln, Germany", "area": 405, "inhabitants": 1_083_000,
         "bounding_box": [6.772530403000076, 50.83044939600006, 7.162027995000074, 51.08497434000003],
         "transport_association": "vrs"},
        {"name": "leipzig", "query": "Leipzig, Germany", "area": 297, "inhabitants": 597_000,
         "bounding_box": [12.236881307029405, 51.238535279757826, 12.542606999586994, 51.448066882712645],
         "transport_association": "vms"},
        {"name": "muenchen", "query": "München, Germany", "area": 310, "inhabitants": 1_488_000,
         "bounding_box": [11.36087720838895, 48.06223277978042, 11.723082533270206, 48.24814577602209],
         "transport_association": "mvv"},
        {"name": "muenster", "query": "Münster, Germany", "area": 303, "inhabitants": 316_000,
         "bounding_box": [7.473962942770497, 51.840191151329854, 7.774221787742102, 52.060175509627584],
         "transport_association": "nwl "},
        {"name": "potsdam", "query": "Potsdam, Germany", "area": 188, "inhabitants": 182_000,
         "bounding_box": [12.888410253169791, 52.342942127472284, 13.165897844431854, 52.51476310782476],
         "transport_association": "vbb"},
        {"name": "stuttgart", "query": "Stuttgart, Germany", "area": 207, "inhabitants": 630_000,
         "bounding_box": [9.03899379817525, 48.69015070969232, 9.315387276070416, 48.86724862272663],
         "transport_association": "vvs"},
        {"name": "wuppertal", "query": "Wuppertal, Germany", "area": 168, "inhabitants": 355_000,
         "bounding_box": [7.01407471400006, 51.165736174000074, 7.313426359000061, 51.31809703300007],
         "transport_association": "vrr"},
    ]

    def get_city_by_name(self, name):
        for city in self.cities:
            if city["name"] == name:
                return city

        return None