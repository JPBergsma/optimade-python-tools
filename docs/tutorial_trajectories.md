## Setting up an OPTIMADE Trajectory database.

The tutorial explains how to set up an OPTIMADE server for trajectory data.
The code linked to here matches the trajectory endpoint as described in [https://github.com/JPBergsma/OPTIMADE/blob/JPBergsma_add_Trajectories/optimade.rst](https://github.com/JPBergsma/OPTIMADE/blob/JPBergsma_add_Trajectories/optimade.rst) and discussed in [OPTIMADE PR#377](https://github.com/Materials-Consortia/OPTIMADE/pull/377):
This corresponds to [version 1.1 of the OPTIMADE specification](https://github.com/Materials-Consortia/OPTIMADE/releases/tag/v1.1.0).
The trajectory endpoint is however still under development and there will probably be significant changes before it is merged with the main OPTIMADE specification.  

The optimade-python-tools support both [MongoDB](https://www.mongodb.com) and [Elasticsearch](https://www.elastic.co/elasticsearch) backends.
Other backends can be used as well, but will require creating a custom filtertransformer for converting the query into a backend compatible format and a custom entry_collections object for interacting with the database backend.
In this tutorial we will use an Ubuntu like linux distribution with MongoDB as the backend.
At the bottem there is a troubleshooting section.

### Aquiring the trajectory version of the optimade python tools

The first step is to install the optimade python tools.
Here we briefly describe the steps required to install the trajectory branch of the optimade python tools.
You can find more details in the installation instructions described in [INSTALL.md](https://github.com/JPBergsma/optimade-python-tools/blob/optimade_python_tools_trajectory_0.1/INSTALL.md).
You will however need to use the code found on GitHub at [https://github.com/JPBergsma/optimade-python-tools/tree/optimade_python_tools_trajectory_0.1](https://github.com/JPBergsma/optimade-python-tools/tree/optimade_python_tools_trajectory_0.1)
If you only want to use the optimade python tools as a library you should use: `pip install git+https://github.com/JPBergsma/optimade-python-tools.git@optimade_python_tools_trajectory_0.1`.
In this tutorial we are however describing how to set up your own database for sharing trajectory data.
In that case it is better to clone the repository and create your own branch from the [optimade_python_tools_trajectory_0.1](https://github.com/JPBergsma/optimade-python-tools/tree/optimade_python_tools_trajectory_0.1) branch.  

If you already have a GitHub account setup you can clone the repository with: `git clone --recursive git@github.com:JPBergsma/optimade-python-tools.git`
Without GitHub account you can use `git clone --recursive https://github.com/JPBergsma/optimade-python-tools.git`
Next you should switch to the version 0.1 branch with `git switch optimade-python-tools-trajectory-0.1`

### Conda

You may now want to set up a separate conda environment so there can't be a version conflict between the dependencies of different python programs.  
See the instructions on how to install (mini)conda here: https://conda.io/projects/conda/en/stable/user-guide/install/index.html

If you use conda you can create a separate environment using: `conda create -n optimade-traj python=3.10`
You can also use Python versions 3.8 and 3.9.  
You can activate the conda environment with: `conda activate optimade-traj`


### Install the trajectory version of the optimade python tools

Next, you can install the local version of this package by going into the optimade-python-tools folder and running `pip install -e .[server]`.
By using the -e flag


### Installing MongoDB

The installation instructions for MongoDB can be found at [https://www.mongodb.com/docs/manual/installation/](https://www.mongodb.com/docs/manual/installation/)
The community edition is good enough for our purpose.
#TODO lookup how to setup mongodb it automatically starts at reboot.

### Setup the config file

The next step is setting up the configuration file ".optimade.json".
The default location is in the users home directory, i.e "~/.optimade.json".
More information and alternative ways for setting up the configuration parameters can be found in the [configuration.md](https://github.com/JPBergsma/optimade-python-tools/blob/optimade_python_tools_trajectory_0.1/docs/configuration.md) file.
An example configuration file "optimade_config.json" is contained in the package and can be used as starting point for creating your own configuration file.
If you are setting up a new database backend the important parameters to set are:

* insert_test_data:
  * description: This value needs to be set to false, otherwise the test data will be inserted in the database you are trying to construct.
  * type: boolean

* database_backend:
  * description: The type of backend that is used. the options are: "elastic" for the elasticsearch backend, "mongodb" for the MongoDB backend and "mongomock" for the test backend.
  In this tutorial we use MongoDB, so it should be set to "mongodb".
  * type: string

* base_url:
  * description: The url at which you will serve the database.
  * type: string

* provider:
  * description: This field contains information about the organization that provides the data base.
  * type: dictionary
  * keys:
    * name:
      * description: The name of the organization providing the database.
      * type: string
    * description:
      * description: A description of the organisation that provides the database.
      * type: string
    * prefix:
      * description: An abbreviation of the name of the database provider with an underscore on each side. e.g. "\_exmpl_". This is used as a prefix for fields in the database that are not described by the optimade standard, but have instead stead been defined by the database provider.
      * type: string  
    * homepage:
      * description: A Url for the website of the provider.
      * type: string

* provider_fields:
  * description: In this dictionary database fields that are specific to this provider are defined. You can remove the entries that
  * type: dictionary
    * keys: Valid keys are the names of the types of endpoints ("links", "references", "structures", "trajectories") that are on this server.  
    * values: A list with a dictionary for each database specific property.
      * keys:
        * name:
          * description: The name of the field as it should be presented in the OPTIMADE response.
          * type: string
        * type:
          * description: The JSON type of the field. possible values are: "boolean", "object" (for an OPTIMADE dictionary), "array" (for an OPTIMADE list), "number" (for an OPTIMADE float), "string", and "integer".
          * type: string
        * unit:
          * description: The unit belonging to the property as described in [GNU Units version 2.22](https://www.gnu.org/software/units/)
          * type: string
        * description:
          * description: A description of the property.
          * type: string

* length_aliases:
  * description: This property maps list properties to integer properties that define the length of those lists.
    For example elements -> nelements. This dictionary must refer to the API fields. For database specific fields the field names must thus be prepended with the database specific prefix.
  * type: dictionary of dictionaries.
  * keys: The names of the entrypoints available on this server. i.e. ["links", "references", "structures", "trajectories"]
  * values: A dictionary with the name of the list field as key and the field corresponding to the length of this list as the value.

* enabled_response_formats
  * description: The supported output formats. JSON is the default output format for optimade. It however does not support storing binary numbers and as a result the response for trajectories can become quite large.
    Therefore, we have added experimental support for the hdf5 format. This will make the responses much smaller when returning large amounts of numerical data, but there is also some extra overhead per field, so for entries without large numerical fields JSON can be more efficient.
    Valid values are: "json" and "hdf5".
  * type: List of strings

* max_response_size:
  * description: Approximately the maximum size of a response for a particular response format.
    The optimade python tools will try to estimate the size of each frame that is to be returned and subsequently try to calculate the number of frames that can be returned in a single response.
    The final file can be larger if the estimate was poor.
  * type: Dictionary
  * keys: The names of the different supported return formats.
  * values: An integer containing the maximum size of the response in megabytes.

More parameters can be found by checking the `ServerConfig` class defined in `optimade.server.config.py`, which are useful if you already have a pre-existing database or want to customize the setup of the MongoDB database.


### Loading trajectory data into mongo DB

The next step is to load the data that is needed to create valid OPTIMADE responses into mongo DB.
A small example script to generate a MongoDB entry from a trajectory file can be found on [https://github.com/JPBergsma/Export_traj_to_mongo](https://github.com/JPBergsma/Export_traj_to_mongo)
It uses the [MDanalysis](https://docs.mdanalysis.org/stable/index.html) package to read the trajectory files.
The supported file types are listed on: [https://userguide.mdanalysis.org/stable/formats/index.html](https://userguide.mdanalysis.org/stable/formats/index.html)
It can be downloaded with `git clone https://github.com/JPBergsma/Export_traj_to_mongo.git`
And installed with `pip install -e <path to Export_traj_to_mongo>`
You can use the same environment as before.

You can use this script to load the trajectory data into your database.

Instructions on how to run this script can be found in the accompanying [README.md](https://github.com/JPBergsma/Export_traj_to_mongo/blob/master/README.md) file.

### Validation

To test the setup up to this point you can go to optimade-python-tools folder and run:
`uvicorn optimade.server.main:app --reload --port=5000`

### deployment

By adding the --reload flag the server is automatically restarted when the code of the optimade python tools is changed.

If you are satisfied with how things are working you can run the server with:

### Register prefix





### Troubleshooting

#### mongoDB

##### exit code 14

This exit code means that the socket mongoDB wants to use is not available.
This may happen when MongoDB was not terminated properly.
It can be solved by: `$ rm /tmp/mongodb-27017.sock`
(27017 is the default port for mongod)

#### miniconda

If after you have installed conda you get the error that the command cannot be found, it may be that the location of conda has not been added to the PATH variable.
This may be because conda has not been initialized properly.
You can try to use `conda init bash` to initialize conda properly. (If you use a shell other than bash you should replace it with the name of your shell.)

If this does work you can try to add the location of the conda executable to the PATH variable. Various methods to this can be found here: [https://www.baeldung.com/linux/path-variable](https://www.baeldung.com/linux/path-variable)



If you get the error message: "ERROR: Error [Errno 2] No such file or directory 'git'" git still needs to be installed with:  `conda install git`
