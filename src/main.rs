
use pyo3::prelude::*;
//use pyo3::types::IntoPyDict;
use colored::Colorize;
use std::path::PathBuf;

fn main() -> PyResult<()> {
    let mut exedir = std::env::current_exe()?;
    exedir.pop();
    //println!("exedir: {}", exedir.display());
    let curdir = std::env::current_dir()?;
    //println!("curdir: {}", curdir.display());

    if let Some(path) = std::env::var_os("PATH") {
        let mut paths = std::env::split_paths(&path).collect::<Vec<_>>();
        paths.push(PathBuf::from(format!("{}/python/windows/x64", curdir.display())));
        paths.push(PathBuf::from(format!("{}/python/windows/x64", exedir.display())));
        let new_path = std::env::join_paths(paths).unwrap();
        std::env::set_var("PATH", &new_path);
        //println!("new path: {:?}", new_path);
    }

    Python::with_gil(|py| {        
        
        let sys = py.import_bound("sys")?;
        let version: String = sys.getattr("version")?.extract()?;        
        println!("I'm Python {}", version);
        
        let syspath = sys.getattr("path")?;
        let append = syspath.getattr("append")?;
        append.call1((exedir.clone(),))?;
        append.call1((format!("{}/python/windows/x64", exedir.display()),))?;
        //append.call1((format!("{}/python/windows/x64/Lib", exedir.display()),))?;
        //append.call1((format!("{}/python/windows/x64/Lib/site-packages", exedir.display()),))?;
        append.call1((format!("{}/python", exedir.display()),))?;
        append.call1((format!("{}/python/plugin", exedir.display()),))?;
        append.call1((curdir.clone(),))?;
        append.call1((format!("{}/python", curdir.display()),))?;
        append.call1((format!("{}/python/plugin", curdir.display()),))?;
        append.call1((format!("{}/python/windows/x64", curdir.display()),))?;
        //append.call1((format!("{}/python/windows/x64/Lib", curdir.display()),))?;
        append.call1((format!("{}/python/windows/x64/Lib/site-packages", curdir.display()),))?;
        
        let path: Vec<String> = syspath.extract()?;
        println!("path: {:?}", path);

        let plugin = py.import_bound("plugin")?;
        let modules: Vec<String> = plugin.getattr("module_list")?.extract()?;
        //println!("modules: {:?}", modules);
        
        for m in modules.iter() {
            let t = py.import_bound(&m[..])?;
            let result: String = t.getattr("test")?.call0()?.extract()?;
            match &result[..] {
                "PASS" => println!("{}: {}", m, result.green()),
                "FAIL" => println!("{}: {}", m, result.red()),
                &_ => todo!(),
            }            
        }

        let setupssh = py.import_bound("setupssh")?;
        let userhost = "fedora@192.168.64.3";
        let result: String = setupssh.getattr("testssh")?.call1((userhost,))?.extract()?;
        println!("result: {}", result);

        
        Ok(())
    })
}