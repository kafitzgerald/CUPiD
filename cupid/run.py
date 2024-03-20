#!/usr/bin/env python

import click
import os
from glob import glob
import papermill as pm
import intake
import cupid.util
import cupid.timeseries
from dask.distributed import Client
import dask
import time
import ploomber
import yaml

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--serial", "-s", is_flag=True, help="Do not use LocalCluster objects")
@click.option(
    "--time-series",
    "-ts",
    is_flag=True,
    help="Run time series generation scripts prior to diagnostics",
)
@click.argument("config_path")
def run(config_path, serial=False, time_series=False):
    """
    Main engine to set up running all the notebooks.
    """

    # Get control structure
    control = cupid.util.get_control_dict(config_path)
    cupid.util.setup_book(config_path)

    if time_series:
        config_timeseries_contents = control["timeseries"]

        # general timeseries arguments for all components
        num_procs = config_timeseries_contents["num_procs"]

        print("calling cam timeseries generation")
        # cam timeseries generation
        cupid.timeseries.create_time_series(
            "cam",
            config_timeseries_contents["atm_vars"],
            config_timeseries_contents["derive_vars_cam"],
            [config_timeseries_contents["case_name"]],  # could also grab from compute_notebooks section of config file
            config_timeseries_contents["atm_hist_str"],
            [config_contents["global_params"]["CESM_output_dir"] + "/" + config_timeseries_contents["case_name"] + "/atm/hist/"],  # could also grab from compute_notebooks section of config file
            [config_contents["global_params"]["CESM_output_dir"]+'/'+config_timeseries_contents['case_name']+'/atm/proc/tseries/'],
            # Note that timeseries output will eventually go in /glade/derecho/scratch/${USER}/archive/${CASE}/${component}/proc/tseries/
            config_timeseries_contents["ts_done"],
            config_timeseries_contents["overwrite_ts"],
            config_timeseries_contents["atm_start_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.start_date
            config_timeseries_contents["atm_end_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.end_date
            "lev",
            num_procs,
            serial,
        )

        print("calling lnd timeseries generation")
        # lnd timeseries generation
        cupid.timeseries.create_time_series(
            "lnd",
            config_timeseries_contents["lnd_vars"],
            config_timeseries_contents["derive_vars_lnd"],
            [config_timeseries_contents["case_name"]],  # could also grab from compute_notebooks section of config file
            config_timeseries_contents["lnd_hist_str"],
            [config_contents["global_params"]["CESM_output_dir"] + "/" + config_timeseries_contents["case_name"] + "/lnd/hist/"],  # could also grab from compute_notebooks section of config file
            [config_contents["global_params"]["CESM_output_dir"]+'/'+config_timeseries_contents['case_name']+'/lnd/proc/tseries/'],
            # Note that timeseries output will eventually go in /glade/derecho/scratch/${USER}/archive/${CASE}/${component}/proc/tseries/
            config_timeseries_contents["ts_done"],
            config_timeseries_contents["overwrite_ts"],
            config_timeseries_contents["lnd_start_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.start_date
            config_timeseries_contents["lnd_end_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.end_date
            "lev", # TODO: land group will need to change this!
            num_procs,
            serial,
        )

        print("calling ocn timeseries generation")
        # ocn timeseries generation
        cupid.timeseries.create_time_series(
            "ocn",
            config_timeseries_contents["ocn_vars"],
            config_timeseries_contents["derive_vars_ocn"],
            [config_timeseries_contents["case_name"]],  # could also grab from compute_notebooks section of config file
            config_timeseries_contents["ocn_hist_str"],
            [config_contents["global_params"]["CESM_output_dir"] + "/" + config_timeseries_contents["case_name"] + "/ocn/hist/"],  # could also grab from compute_notebooks section of config file
            [config_contents["global_params"]["CESM_output_dir"]+'/'+config_timeseries_contents['case_name']+'/ocn/proc/tseries/'],
            # Note that timeseries output will eventually go in /glade/derecho/scratch/${USER}/archive/${CASE}/${component}/proc/tseries/
            config_timeseries_contents["ts_done"],
            config_timeseries_contents["overwrite_ts"],
            config_timeseries_contents["ocn_start_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.start_date
            config_timeseries_contents["ocn_end_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.end_date
            "lev", # TODO: ocean group will need to change this!
            num_procs,
            serial,
        )

        print("calling cice timeseries generation")
        # cice timeseries generation
        cupid.timeseries.create_time_series(
            "cice",
            config_timeseries_contents["cice_vars"],
            config_timeseries_contents["derive_vars_cice"],
            [config_timeseries_contents["case_name"]],  # could also grab from compute_notebooks section of config file
            config_timeseries_contents["cice_hist_str"],
            [config_contents["global_params"]["CESM_output_dir"] + "/" + config_timeseries_contents["case_name"] + "/cice/hist/"],  # could also grab from compute_notebooks section of config file
            [config_contents["global_params"]["CESM_output_dir"]+'/'+config_timeseries_contents['case_name']+'/cice/proc/tseries/'],
            # Note that timeseries output will eventually go in /glade/derecho/scratch/${USER}/archive/${CASE}/${component}/proc/tseries/
            config_timeseries_contents["ts_done"],
            config_timeseries_contents["overwrite_ts"],
            config_timeseries_contents["cice_start_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.start_date
            config_timeseries_contents["cice_end_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.end_date
            "lev", # TODO: cice group will need to change this!
            num_procs,
            serial,
        )

        print("calling glc timeseries generation")
        # glc timeseries generation
        cupid.timeseries.create_time_series(
            "glc",
            config_timeseries_contents["glc_vars"],
            config_timeseries_contents["derive_vars_glc"],
            [config_timeseries_contents["case_name"]],  # could also grab from compute_notebooks section of config file
            config_timeseries_contents["glc_hist_str"],
            [config_contents["global_params"]["CESM_output_dir"] + "/" + config_timeseries_contents["case_name"] + "/glc/hist/"],  # could also grab from compute_notebooks section of config file
            [config_contents["global_params"]["CESM_output_dir"]+'/'+config_timeseries_contents['case_name']+'/glc/proc/tseries/'],
            # Note that timeseries output will eventually go in /glade/derecho/scratch/${USER}/archive/${CASE}/${component}/proc/tseries/
            config_timeseries_contents["ts_done"],
            config_timeseries_contents["overwrite_ts"],
            config_timeseries_contents["glc_start_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.start_date
            config_timeseries_contents["glc_end_years"],  # could get from yaml file in adf_quick_run.parameter_groups.none.config_fil_str, or for other notebooks config files, eg ocean_surface.parameter_gropus.none.mom6_tools_config.end_date
            "lev", # TODO: glc group will need to change this!
            num_procs,
            serial,
        )

    # Grab paths

    run_dir = os.path.realpath(os.path.expanduser(control["data_sources"]["run_dir"]))
    output_dir = run_dir + "/computed_notebooks/" + control["data_sources"]["sname"]
    temp_data_path = run_dir + "/temp_data"
    nb_path_root = os.path.realpath(
        os.path.expanduser(control["data_sources"]["nb_path_root"])
    )

    #####################################################################
    # Managing catalog-related stuff

    # Access catalog if it exists

    cat_path = None

    if "path_to_cat_json" in control["data_sources"]:
        use_catalog = True
        full_cat_path = os.path.realpath(
            os.path.expanduser(control["data_sources"]["path_to_cat_json"])
        )
        full_cat = intake.open_esm_datastore(full_cat_path)

        # Doing initial subsetting on full catalog, e.g. to only use certain cases

        if "subset" in control["data_sources"]:
            first_subset_kwargs = control["data_sources"]["subset"]
            cat_subset = full_cat.search(**first_subset_kwargs)
            # This pulls out the name of the catalog from the path
            cat_subset_name = full_cat_path.split("/")[-1].split(".")[0] + "_subset"
            cat_subset.serialize(
                directory=temp_data_path, name=cat_subset_name, catalog_type="file"
            )
            cat_path = temp_data_path + "/" + cat_subset_name + ".json"
        else:
            cat_path = full_cat_path

    #####################################################################
    # Managing global parameters

    global_params = dict()

    if "global_params" in control:
        global_params = control["global_params"]

    #####################################################################
    # Ploomber - making a DAG

    dag = ploomber.DAG(executor=ploomber.executors.Serial())

    #####################################################################
    # Organizing notebooks - holdover from manually managing dependencies before

    all_nbs = dict()

    for nb, info in control["compute_notebooks"].items():

        all_nbs[nb] = info

    # Setting up notebook tasks

    for nb, info in all_nbs.items():

        global_params["serial"] = serial
        if "dependency" in info:
            cupid.util.create_ploomber_nb_task(
                nb,
                info,
                cat_path,
                nb_path_root,
                output_dir,
                global_params,
                dag,
                dependency=info["dependency"],
            )

        else:
            cupid.util.create_ploomber_nb_task(
                nb, info, cat_path, nb_path_root, output_dir, global_params, dag
            )

    #####################################################################
    # Organizing scripts

    if "compute_scripts" in control:

        all_scripts = dict()

        for script, info in control["compute_scripts"].items():

            all_scripts[script] = info

        # Setting up script tasks

        for script, info in all_scripts.items():

            if "dependency" in info:
                cupid.util.create_ploomber_script_task(
                    script,
                    info,
                    cat_path,
                    nb_path_root,
                    global_params,
                    dag,
                    dependency=info["dependency"],
                )

            else:
                cupid.util.create_ploomber_script_task(
                    script, info, cat_path, nb_path_root, global_params, dag
                )

    # Run the full DAG

    dag.build()

    return None
