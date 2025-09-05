def shortest_destination(travel_times,
                        destinations_gdf=None,
                         to_id_col="to_id",
                         from_id_col="from_id",
                         time_col="travel_time"):
    return travel_times.sort_values(time_col).drop_duplicates(to_id_col)
