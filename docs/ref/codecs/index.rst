######
Codecs
######

To load and save data from external data files Odin provides a number of codecs to facilitate the process.

Often the API used by the codec mirrors or extends the API provided by the library the Odin extends on. For example for
JSON data Odin provides the same ``load``, ``loads`` style interface.

.. toctree::
   :maxdepth: 2

   csv_codec
   json_codec
   yaml_codec
   msgpack_codec
   xml_codec
