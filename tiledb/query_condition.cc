
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>

#include <exception>

#define TILEDB_DEPRECATED
#define TILEDB_DEPRECATED_EXPORT

#include "util.h"
#include <tiledb/tiledb> // C++

#if TILEDB_VERSION_MAJOR == 2 && TILEDB_VERSION_MINOR >= 2

#if !defined(NDEBUG)
#include "debug.cc"
#endif

namespace tiledbpy {

using namespace std;
using namespace tiledb;
namespace py = pybind11;
using namespace pybind11::literals;

class PyQueryCondition {

private:
  Context ctx_;
  shared_ptr<QueryCondition> qc_;

public:
  tiledb_ctx_t *c_ctx_;

public:
  PyQueryCondition() = delete;

  PyQueryCondition(const string &attribute_name, const string &condition_value,
                   tiledb_query_condition_op_t op, py::object ctx) {
    try {
      init_private_attrs(ctx);
      qc_->init(attribute_name, condition_value, op);
    } catch (TileDBError &e) {
      TPY_ERROR_LOC(e.what());
    }
  }

  template <typename T>
  PyQueryCondition(const string &attribute_name, T condition_value,
                   tiledb_query_condition_op_t op, py::object ctx) {
    try {
      init_private_attrs(ctx);
      qc_->init(attribute_name, &condition_value, sizeof(condition_value), op);
    } catch (TileDBError &e) {
      TPY_ERROR_LOC(e.what());
    }
  }

  void init_private_attrs(py::object ctx) {
    if (ctx.is(py::none())) {
      auto tiledblib = py::module::import("tiledb");
      auto default_ctx = tiledblib.attr("default_ctx");
      ctx = default_ctx();
    }

    tiledb_ctx_t *c_ctx_ = (py::capsule)ctx.attr("__capsule__")();

    if (c_ctx_ == nullptr)
      TPY_ERROR_LOC("Invalid context pointer!");

    ctx_ = Context(c_ctx_, false);

    qc_ = shared_ptr<tiledb::QueryCondition>(new QueryCondition(ctx_));
  }

  QueryCondition
  combine(const QueryCondition &rhs,
          tiledb_query_condition_combination_op_t combination_op) const {
    return qc_->combine(rhs, combination_op);
  }
}; // namespace tiledbpy

PYBIND11_MODULE(_query_condition, m) {
  py::class_<PyQueryCondition>(m, "qc")
      .def(py::init<const string &, const string &, tiledb_query_condition_op_t,
                    py::object>(),
           py::arg("attribute_name"), py::arg("condition_value"),
           py::arg("tiledb_query_condition_op_t"), py::arg("ctx") = py::none())
      .def(py::init<const string &, double, tiledb_query_condition_op_t,
                    py::object>(),
           py::arg("attribute_name"), py::arg("condition_value"),
           py::arg("tiledb_query_condition_op_t"), py::arg("ctx") = py::none())
      .def(py::init<const string &, float, tiledb_query_condition_op_t,
                    py::object>(),
           py::arg("attribute_name"), py::arg("condition_value"),
           py::arg("tiledb_query_condition_op_t"), py::arg("ctx") = py::none())
      .def(py::init<const string &, int, tiledb_query_condition_op_t,
                    py::object>(),
           py::arg("attribute_name"), py::arg("condition_value"),
           py::arg("tiledb_query_condition_op_t"), py::arg("ctx") = py::none())

      .def("combine", &PyQueryCondition::combine, py::arg("rhs"),
           py::arg("combination_op"));

  py::enum_<tiledb_query_condition_op_t>(m, "tiledb_query_condition_op_t",
                                         py::arithmetic())
      .value("TILEDB_LT", TILEDB_LT)
      .value("TILEDB_LE", TILEDB_LE)
      .value("TILEDB_GT", TILEDB_GT)
      .value("TILEDB_GE", TILEDB_GE)
      .value("TILEDB_EQ", TILEDB_EQ)
      .value("TILEDB_NE", TILEDB_NE)
      .export_values();
}
}; // namespace tiledbpy

#endif