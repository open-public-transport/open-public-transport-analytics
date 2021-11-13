import pandas as pd
import geopandas as gpd


def get_centroid(geodataframe):
    return geodataframe.centroid


def transform_zipcodes_to_geometries(df_inhab, df_geometry):
    '''
    only for two dataframes oder shpaes with the information of zip codes and the other with inhab/populaiton information

    Parameters:
    -----------
    df_inhab: pandas.DataFrame
        DataFrame with ID, ZipCodes and Inhabitant number 

    Retruns:
    -----------
    zip_and_geom: GeoJson
        with Geometry Object for every Zipcode
    '''
    return 