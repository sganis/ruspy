use pyo3::prelude::*;
//use pyo3::types::IntoPyDict;

fn main() -> PyResult<()> {
    Python::with_gil(|py| {
        let sys = py.import_bound("sys")?;
        let version: String = sys.getattr("version")?.extract()?;
        
        //let locals = [("os", py.import_bound("os")?)].into_py_dict_bound(py);
        //let code = "os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'";
        //let user: String = py.eval_bound(code, None, Some(&locals))?.extract()?;

        println!("I'm Python {}", version);
        
        let mut exedir = std::env::current_exe()?;
        exedir.pop();
        //println!("exedir: {}", exedir.display());
        let curdir = std::env::current_dir()?;
        //println!("curdir: {}", curdir.display());
        let syspath = sys.getattr("path")?;
        let append = syspath.getattr("append")?;
        append.call1((exedir,))?;
        append.call1((curdir.clone(),))?;
        append.call1((format!("{}/plugins", curdir.display()),))?;
        //let path: Vec<String> = syspath.extract()?;
        //println!("path: {:?}", path);

        let plugins = py.import_bound("plugins")?;
        let modules: Vec<String> = plugins.getattr("module_list")?.extract()?;
        //println!("modules: {:?}", modules);
        
        for m in modules.iter() {
            let t = py.import_bound(&m[..])?;
            let result: String = t.getattr("test")?.call0()?.extract()?;
            println!("{}: {}", m, result);
        }

        
        Ok(())
    })
}