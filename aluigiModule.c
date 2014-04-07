#include <Python.h>

int enctype2_encoder(unsigned char *key, unsigned char *data, int size);

static PyObject* encodeList(PyObject* self, PyObject* args) {
	unsigned char *key, *data;
	int size;
	
	if (!PyArg_ParseTuple(args, "syi", &key, &data, &size)) {
		return NULL;
	}
	
	enctype2_encoder(key, data, size);
	
	return Py_BuildValue("y", data);
}

static PyMethodDef aluigiMethods[] = {
	{"encodeList", encodeList, METH_VARARGS},
	{NULL, NULL}
};

static struct PyModuleDef aluigiModule = {
	PyModuleDef_HEAD_INIT,
	"aluigi",
	NULL,
	-1,
	aluigiMethods
};

PyMODINIT_FUNC PyInit_aluigi() {
	return PyModule_Create(&aluigiModule);
}

