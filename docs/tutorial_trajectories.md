## Setting up an OPTIMADE Trajectory database.

The tutorial explains how to set up an OPTIMADE server for trajectory data.
The code linked to here matches the trajectory endpoint as described in [https://github.com/JPBergsma/OPTIMADE/blob/Trajectory_proposal_v0.1/optimade.rst](https://github.com/JPBergsma/OPTIMADE/blob/Trajectory_proposal_v0.1/optimade.rst) and discussed in [OPTIMADE PR#377](https://github.com/Materials-Consortia/OPTIMADE/pull/377):
This corresponds to [version 1.1 of the OPTIMADE specification](https://github.com/Materials-Consortia/OPTIMADE/releases/tag/v1.1.0).
The trajectory endpoint is however still under development and there will probably be significant changes before it is merged with the main OPTIMADE specification.  

The optimade-python-tools support both [MongoDB](https://www.mongodb.com) and [Elasticsearch](https://www.elastic.co/elasticsearch) backends.
Other backends can be used as well, but will require creating a custom filtertransformer for converting the query into a backend compatible format and a custom entry_collections object for interacting with the database backend.
In this tutorial, we will use an Ubuntu like Linux distribution with MongoDB as the backend.
At the bottem there is a troubleshooting section.

### Acquiring the trajectory version of the optimade python tools

The first step is to install the optimade python tools.
Here, we briefly describe the steps required to install the trajectory branch of the optimade python tools.
You can find more details in the installation instructions described in [INSTALL.md](https://github.com/JPBergsma/optimade-python-tools/blob/optimade_python_tools_trajectory_0.1/INSTALL.md).
You will however need to use the code found on GitHub at [https://github.com/JPBergsma/optimade-python-tools/tree/optimade_python_tools_trajectory_0.1](https://github.com/JPBergsma/optimade-python-tools/tree/optimade_python_tools_trajectory_0.1)
If you only want to use the optimade python tools as a library you can use: `pip install git+https://github.com/JPBergsma/optimade-python-tools.git@optimade_python_tools_trajectory_0.1`.
In this tutorial, we are however describing how to set up your own database for sharing trajectory data.
In that case it is better to clone the repository and create your own branch from the [optimade_python_tools_trajectory_0.1](https://github.com/JPBergsma/optimade-python-tools/tree/optimade_python_tools_trajectory_0.1) branch.
This way you can easily make modifications to the code when you want to change the behaviour of your server later on.

If you already have a GitHub account setup you can clone the repository with: `git clone --recursive git@github.com:JPBergsma/optimade-python-tools.git`
Without GitHub account you can use `git clone --recursive https://github.com/JPBergsma/optimade-python-tools.git`
Next you should switch to the version 0.1 branch with `git switch optimade-python-tools-trajectory-0.1`

### Conda

You may now want to set up a separate Conda environment so there can't be a version conflict between the dependencies of different python programs.  
See the instructions on how to install (Mini)Conda here: https://conda.io/projects/conda/en/stable/user-guide/install/index.html

If you use Conda you can create a separate environment using: `conda create -n optimade-traj python=3.10`
You can also use Python versions 3.8 and 3.9.  
You can activate the Conda environment with: `conda activate optimade-traj`


### Install the trajectory version of the optimade python tools

Next, you can install the local version of this package by going into the optimade-python-tools folder and running `pip install -e .[server]`.

### Installing MongoDB

The installation instructions for MongoDB can be found at [https://www.mongodb.com/docs/manual/installation/](https://www.mongodb.com/docs/manual/installation/)
The community edition is good enough for our purpose.
To automatically run the mongod daemon when the machine is booted, you can run: `systemctl enable mongod.service`

### Set up the config file

The next step is setting up the configuration file ".optimade.json".
The default location is in the user's home directory, i.e "~/.optimade.json".
More information and alternative ways for setting up the configuration parameters can be found in the [configuration.md](https://github.com/JPBergsma/optimade-python-tools/blob/optimade_python_tools_trajectory_0.1/docs/configuration.md) file.
An example configuration file "optimade_config.json" is contained in the package and can be used as starting point for creating your own configuration file.
If you are setting up a new database backend, the important parameters to set are:

* insert_test_data:
  * description: This value needs to be set to false, otherwise the test data will be inserted in the database you are trying to construct.
  * type: boolean

* database_backend:
  * description: The type of backend that is used. the options are: "elastic" for the Elasticsearch backend, "mongodb" for the MongoDB backend and "mongomock" for the test backend.
  In this tutorial, we use MongoDB, so it should be set to "mongodb".
  * type: string

* base_url:
  * description: The URL at which you will serve the database.
  If you are only testing the optimade python tools locally, you can use: "http://localhost:5000".
  * type: string

* provider:
  * description: This field contains information about the organization that provides the database.
  * type: dictionary
  * keys:
    * name:
      * description: The name of the organization providing the database.
      * type: string
    * description:
      * description: A description of the organization that provides the database.
      * type: string
    * prefix:
      * description: An abbreviation of the name of the database provider with an underscore on each side. e.g. "\_exmpl_".
      This is used as a prefix for fields in the database that are not described by the optimade standard, but have instead stead been defined by the database provider.
      * type: string  
    * homepage:
      * description: A URL to the website of the provider.
      * type: string

* provider_fields:
  * description: In this dictionary, fields that are specific to this provider are defined.
  * type: dictionary
    * keys: Valid keys are the names of the types of endpoints ("links", "references", "structures", "trajectories") that are on this server.
    * values: A list with a dictionary for each database specific field/property that has been defined for the endpoint specified by the key.
      * keys: The sub-dictionaries describing the database specific properties/fields can contain the following keys:
        * name:
          * description: The name, without prefix, of the field as it should be presented in the OPTIMADE response.
          * type: string
        * type:
          * description: The JSON type of the field.
          Possible values are: "boolean", "object" (for an OPTIMADE dictionary), "array" (for an OPTIMADE list), "number" (for an OPTIMADE float), "string", and "integer".
          * type: string
        * unit:
          * description: The unit belonging to the property as described in [GNU Units version 2.22](https://www.gnu.org/software/units/)
          * type: string
        * description:
          * description: A description of the property.
          * type: string

* length_aliases:
  * description: This property maps list properties to integer properties that define the length of those lists.
    For example: elements -> nelements.
    The standard aliases are applied first, so this dictionary must refer to the API fields, not the database fields.
  * type: dictionary of dictionaries.
  * keys: The names of the entrypoints available on this server. i.e. ["links", "references", "structures", "trajectories"]
  * values: A dictionary with the name of the list field as the key and the field corresponding to the length of this list as the value.

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

The next step is to load the data that is needed to create valid OPTIMADE responses into the Mongo database.
A small example script to generate a MongoDB entry from a trajectory file can be found on [https://github.com/JPBergsma/Export_traj_to_mongo](https://github.com/JPBergsma/Export_traj_to_mongo)
It uses the [MDanalysis](https://docs.mdanalysis.org/stable/index.html) package to read the trajectory files.
The supported file types are listed on: [https://userguide.mdanalysis.org/stable/formats/index.html](https://userguide.mdanalysis.org/stable/formats/index.html)
It can be downloaded with `git clone https://github.com/JPBergsma/Export_traj_to_mongo.git`
And installed with `pip install -e <path to Export_traj_to_mongo>`
You can use the same environment as before.

You can use this script to load the trajectory data into your database.

Instructions on how to run this script can be found in the accompanying [README.md](https://github.com/JPBergsma/Export_traj_to_mongo/blob/master/README.md) file.

### Validation

To test the setup, you can go to optimade-python-tools folder and run:
`uvicorn optimade.server.main:app --reload --port=5000`
This will start the optimade server.
Next, you can run `optimade-validator http://localhost:5000` to validate the setup of your database.
At the moment, the validator may still give a "'StrictFieldInfo' object is not subscriptable" error. You can ignore this error for now.
Errors under INTERNAL FAILURES indicate problems with the validator itself and not with the server setup. You can report those [here](https://github.com/JPBergsma/optimade-python-tools/issues).
More details about validating your server can be found in [validation.md](https://github.com/JPBergsma/optimade-python-tools/blob/optimade_python_tools_trajectory_0.1/docs/concepts/validation.md).

### Deployment

If you are satisfied with how things are , you can run the server with:
`uvicorn optimade.server.main:app --reload --port=5000 --host=0.0.0.0` for it to be reachable from any IPv4 adress and
`uvicorn optimade.server.main:app --reload --port=5000 --host='::'` for IPv6
By adding the --reload flag, the server is automatically restarted when the code of the optimade python tools is changed.

Uvicorn runs as a single process and thus uses only a single cpu core.
If you want to run multiple processes, you can use Gunicorn.
Instructions for this on how to set this up can be found on https://fastapi.tiangolo.com/uk/deployment/server-workers/

In many organizations there is a firewall between the internet and the internal network.
You may therefore need to contact the ICT department of your organization to make your server reachable from outside the internal network.
This is also a good opportunity to ask them about extra security measures you may need to take.
e.g. run the server within a container/virtual machine or using nginx.

### Register prefix

Once you have finished setting up your server, you can register your database.
You can find instructions on how to do this here: [https://github.com/Materials-Consortia/providers#requirements-to-be-listed-in-this-providers-list](https://github.com/Materials-Consortia/providers#requirements-to-be-listed-in-this-providers-list)

### Troubleshooting

#### MongoDB

##### exit code 14

This exit code means that the socket MongoDB wants to use is not available.
This may happen when MongoDB was not terminated properly.
It can be solved by: `$ rm /tmp/mongodb-27017.sock`
(27017 is the default port for mongod)

#### (Mini)Conda

If after you have installed Conda you get the error that the command cannot be found, it may be that the location of Conda has not been added to the PATH variable.
This may be because Conda has not been initialized properly.
You can try to use `conda init bash` to initialize Conda properly. (If you use a shell other than bash you should replace it with the name of your shell.)

If you get the error message: "ERROR: Error [Errno 2] No such file or directory 'git'" git still needs to be installed with:  `conda install git`


#### Further help

General questions about OPTIMADE can be asked on the [Matsci forum](https://matsci.org/c/optimade/29).
Bug reports or feature requests about the optimade-python-tools in general can be posted on the optimade-python-tools github page: https://github.com/Materials-Consortia/optimade-python-tools/issues
Issues specific to the trajectory branch of the optimade-python-tools can be posted here: https://github.com/JPBergsma/optimade-python-tools/issues
