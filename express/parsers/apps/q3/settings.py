# q3 writes its main results file as "<outdir>/<prefix>_results.json"
# (see lib/q3/docs/io_reference.md, section 4.1). The prefix is user-configurable,
# so the parser locates the file by this suffix rather than an exact name.
RESULTS_FILE_SUFFIX = "_results.json"

# The q3_dos shell unit of the standata "Density of States - Q3" workflow
# writes the Gaussian-broadened density of states here, in Rydberg units
# (energies_ry, and dos in states/Ry), as returned by q3.io.output_writer.extract_dos.
DENSITY_OF_STATES_FILE = "q3_dos.json"
