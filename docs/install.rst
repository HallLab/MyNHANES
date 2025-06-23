Installation
============

Installing MyNHANES
-------------------

To install the MyNHANES package, you can use ``pip``, the Python package installer. Run the following command in your terminal:

.. code-block:: bash

    pip install mynhanes

Setting Up MyNHANES
-------------------

After installation, you need to set up the environment. Depending on whether you are setting up a local or a remote environment, use one of the following commands:

Local Deployment
^^^^^^^^^^^^^^^^

This command sets up a local SQLite database and initializes it with NHANES baseline data. It also prompts you to create a superuser account for accessing the admin dashboard.

.. code-block:: bash

    python manage.py deploy --deploy local

Remote Deployment
^^^^^^^^^^^^^^^^^

For deploying to a remote server or a specified path, use the following command. Replace ``{path}`` with the path to your target directory on the remote server.

.. code-block:: bash

    python manage.py deploy --deploy remote --path {path}

This will configure the application to use a pre-existing database specified at the given path.

Running the Server
------------------

Once the setup is complete, you can start the local development server to access the NHANES system:

.. code-block:: bash

    python manage.py runserver

This command starts the server, making the application accessible via ``http://localhost:8000`` by default. To access the Django admin interface, navigate to ``http://localhost:8000/admin``.

Further Configuration
---------------------

For further configurations and adjustments, refer to the Django documentation or the additional configuration guides provided with MyNHANES.
