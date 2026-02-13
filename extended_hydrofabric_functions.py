import pandas as pd
import geopandas as gpd
import glob
import re
from shapely.geometry import Point
import os
from tqdm import tqdm
import shutil

# Functions

# ---- fallback tracking ----
fallback1_count = 0
fallback2_count = 0
fallback3_count = 0

fallback1_ids = []
fallback2_ids = []
fallback3_ids = []


def vcat(pattern, subset_dedup=None):
    """Read all CSVs matching pattern and vertically concatenate."""
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No files matched: {pattern}")
    dfs = [pd.read_csv(f) for f in files]
    out = pd.concat(dfs, ignore_index=True)
    if subset_dedup:
        out = out.drop_duplicates(subset=subset_dedup)
    return out


def normalize_name(name):
    if not isinstance(name, str):
        return ''

    original = name.lower().strip()
    name = original

    # Remove directional prefixes
    directional_prefixes = ['east ', 'west ', 'north ', 'south ', 'upper ', 'lower ']
    for p in directional_prefixes:
        if name.startswith(p):
            name = name[len(p):]

    # Remove hydrologic suffixes
    suffixes = [' river', ' creek', ' stream', ' wash', ' arroyo', ' fork', ' branch']
    for s in suffixes:
        if name.endswith(s):
            name = name[:-len(s)]

    name = name.strip()

    # If everything was stripped, keep the original string
    if name == '':
        return original

    return name


def safe_str(x):
    return "" if pd.isna(x) or x is None else str(x)


def normalize_name_res(name):
    original = name.lower().strip()
    name = original
    if not name:
        return name
    prefixes = [
        'east ', 'west ', 'north ', 'south ', 'upper ', 'lower ',
        'middle fork of ', 'middle ', 'offstream ', 'off-stream ',
    ]
    for p in prefixes:
        if name.startswith(p):
            name = name[len(p):]
    suffixes = [' river', ' creek', ' stream', ' wash', ' arroyo', ' fork', ' branch', ' canal']
    for s in suffixes:
        if name.endswith(s):
            name = name[:-len(s)]

        # If everything was stripped, keep the original string
        if name == '':
            return original

    return name.strip()


def closest_segment_POD(point, gdf):
    global fallback3_count, fallback3_ids, fallback4_count, no_link_count, no_link_ids, no_link_records
    point_geom = point.geometry
    point_gnis_id = point['SOURCE_GNIS_ID']
    point_gnis_id_raw = str(point['Source GNIS ID Raw']).strip().lower()
    point_source = str(point['WATER_SOURCE']).strip().lower()
    pod_id = point.get('WDID', None)

    # Case 1: Use GNIS ID directly
    if pd.notna(point_gnis_id) and point_gnis_id_raw != 'tbd':
        matching_segments = gdf[gdf['gnis_id'] == point_gnis_id].copy()
        if matching_segments.empty:
            matching_segments = gdf.copy()
        matching_segments['distance'] = matching_segments.distance(point_geom)
        closest_idx = matching_segments['distance'].idxmin()
        return matching_segments.loc[closest_idx]

    # Case 2: Use normalized Water Source Name
    elif point_source != 'tbd':

        normalized_source = normalize_name(point_source)
        candidate_segments = gdf[gdf['gnis_name'].notna()].copy()

        def name_matches(gnis):
            return normalize_name(gnis) == normalized_source

        candidate_segments['name_match'] = candidate_segments['gnis_name'].apply(name_matches)
        matched_segments = candidate_segments[candidate_segments['name_match']]

        if matched_segments.empty:
            matched_segments = gdf[gdf['streamorde'].fillna(0) >= 3].copy()
            fallback3_count += 1
            if pod_id is not None:
                fallback3_ids.append(pod_id)

        matched_segments = matched_segments.assign(
            distance=matched_segments.geometry.distance(point_geom)
        )
        closest_idx = matched_segments['distance'].idxmin()
        return matched_segments.loc[closest_idx]

    # Case 3: Fallback to streamorde >= 3
    else:
        fallback_segments = gdf[gdf['streamorde'].fillna(0) >= 3].copy()
        fallback3_count += 1
        if pod_id is not None:
            fallback3_ids.append(pod_id)

        if fallback_segments.empty:
            fallback4_count += 1

            # record for visual inspection
            no_link_count += 1
            if pod_id is not None:
                no_link_ids.append(pod_id)

            no_link_records.append({
                "WDID": pod_id,
                "geometry": point_geom,
                "SOURCE_GNIS_ID": point_gnis_id,
                "Source GNIS ID Raw": point.get("Source GNIS ID Raw", None),
                "WATER_SOURCE": point.get("WATER_SOURCE", None),
                "reason": "no_streamorde>=3_segment"
            })

            # DO NOT connect to any segment
            return None

        fallback_segments['distance'] = fallback_segments.distance(point_geom)
        closest_idx = fallback_segments['distance'].idxmin()
        return fallback_segments.loc[closest_idx]


def closest_segment_func(point, gdf):
    lake_segments = gdf[gdf['wbareatype'] == 'LakePond'].copy()
    lake_segments.loc[:, 'distance'] = lake_segments.distance(point)
    closest_idx = lake_segments['distance'].idxmin()
    return lake_segments.loc[closest_idx]


res_fallback_counter = 0


def closest_segment_func2(point, gdf, radius_m=1000):
    global res_fallback_counter
    """
    Link a reservoir to:
      1) nearest LakePond segment within radius_m, preferring name matches
      2) if no LakePond within radius_m: closest segment (any wbareatype) within radius_m
      3) if no segments at all within radius_m: closest segment anywhere (any type)

    Assumes gdf and point are in a projected CRS with meters as units.
    """

    # --- 0) spatial restriction: ONLY within radius_m ---
    buf = gpd.GeoSeries([point.geometry], crs=gdf.crs).buffer(radius_m).iloc[0]
    local = gdf[gdf.intersects(buf)].copy()

    # If nothing is within 1000 m, optionally fall back to global nearest (any type)
    if local.empty:
        # If you prefer returning None instead, replace this whole block with `return None`
        all_segs = gdf.copy()
        if all_segs.empty:
            return None
        all_segs = all_segs.assign(distance=all_segs.geometry.distance(point.geometry))
        res_fallback_counter += 1
        return all_segs.loc[all_segs['distance'].idxmin()]

    # --- 1) Try LakePond logic within radius_m ---
    river_name_norm = normalize_name(point.get('RIVER', ''))

    local_lake = local[local['wbareatype'] == 'LakePond'].copy()

    if not local_lake.empty:
        # Candidate segments: LakePond with a name
        candidate = local_lake[local_lake['gnis_name'].notna()].copy()

        # If there is a usable river name, attempt name matching inside radius
        if river_name_norm and not candidate.empty:
            candidate = candidate.assign(_name_norm=candidate['gnis_name'].apply(normalize_name_res))
            matched = candidate[candidate['_name_norm'] == river_name_norm]

            if matched.empty:
                matched = candidate[candidate['_name_norm'].str.contains(river_name_norm, na=False)]

            if not matched.empty:
                matched = matched.assign(distance=matched.geometry.distance(point.geometry))
                return matched.loc[matched['distance'].idxmin()]

        # No usable name match (or no names): choose nearest LakePond within radius
        local_lake = local_lake.assign(distance=local_lake.geometry.distance(point.geometry))
        return local_lake.loc[local_lake['distance'].idxmin()]

    # --- 2) No LakePond within radius_m -> closest segment (any type) within radius_m ---
    local = local.assign(distance=local.geometry.distance(point.geometry))
    res_fallback_counter += 1
    return local.loc[local['distance'].idxmin()]


def walk_downstream_past_lakepond(start_row, gdf, max_steps=20):
    """
    If start_row is LakePond, walk downstream via tocomid while the downstream
    segment is also LakePond.

    Returns:
      - the first downstream NON-LakePond segment after the LakePond chain, if found
      - otherwise, the last valid segment reached (often the last LakePond)

    Requirements:
      gdf has columns: 'comid', 'tocomid', 'wbareatype'
    """

    if start_row is None:
        return None

    # Build quick lookup: comid -> row (first occurrence)
    # If comid is unique in your layer, this is perfect.
    # If not unique, decide how you want to handle duplicates.
    by_comid = gdf.set_index("comid", drop=False)

    def valid_tocomid(x):
        if x is None or pd.isna(x):
            return None
        try:
            x = int(x)
        except Exception:
            return None
        return None if x == 0 else x

    cur = start_row
    visited = set()

    for _ in range(max_steps):
        # Stop if current isn't LakePond (nothing to do)
        if cur.get("wbareatype", None) != "LakePond":
            return cur

        cur_comid = cur.get("comid", None)
        if cur_comid is not None:
            # cycle guard
            if cur_comid in visited:
                return cur
            visited.add(cur_comid)

        nxt_id = valid_tocomid(cur.get("tocomid", None))
        if nxt_id is None:
            return cur  # terminal/no link

        if nxt_id not in by_comid.index:
            return cur  # downstream segment not present in gdf

        nxt = by_comid.loc[nxt_id]

        # If downstream is not LakePond, return downstream (this is usually what people want)
        if nxt.get("wbareatype", None) != "LakePond":
            return cur

        # Otherwise keep going
        cur = nxt

    # max_steps exceeded (avoid infinite loops)
    return cur