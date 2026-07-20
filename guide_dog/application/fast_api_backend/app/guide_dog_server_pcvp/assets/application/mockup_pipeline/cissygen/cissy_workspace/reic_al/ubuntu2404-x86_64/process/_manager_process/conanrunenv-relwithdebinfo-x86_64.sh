script_folder="/home/reic_al/repositories/guide_dog/application/mockup_pipeline/cissygen/cissy_workspace/reic_al/ubuntu2404-x86_64/process/_manager_process"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
for v in PATH PYTHONPATH LN_DAEMON_START LD_LIBRARY_PATH DYLD_LIBRARY_PATH LN_MESSAGE_DEFINITION_DIRS
do
   is_defined="true"
   value=$(printenv $v) || is_defined="" || true
   if [ -n "$value" ] || [ -n "$is_defined" ]
   then
       echo export "$v='$value'" >> "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
   else
       echo unset $v >> "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
   fi
done

export PATH="/volume/conan_cache/reic_al/.conan2/p/links3e442feaecb49/p/bin:/volume/conan_cache/reic_al/.conan2/p/links11a4a06ea486a/p/bin:/volume/conan_cache/reic_al/.conan2/p/procpc4b894f4e3426/p/bin:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/bin:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/bin:/volume/conan_cache/reic_al/.conan2/p/links2653006da8edf/p/bin:$PATH:/volume/conan_cache/reic_al/.conan2/p/links2653006da8edf/p/bin:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/bin:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/bin:/volume/conan_cache/reic_al/.conan2/p/links3e442feaecb49/p/bin"
export PYTHONPATH="$PYTHONPATH:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/lib/python/site-packages:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/lib/python/site-packages:/volume/conan_cache/reic_al/.conan2/p/links3e442feaecb49/p/lib/python/site-packages"
export LN_DAEMON_START=". /etc/profile && /opt/rmc-build-tools/any/cissy2/bin/linux/cissy run  -w None -p links_and_nodes_runtime/2.8.2@common/stable ln_daemon"
export LD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/links3e442feaecb49/p/lib:/volume/conan_cache/reic_al/.conan2/p/procpc4b894f4e3426/p/lib:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/lib:$LD_LIBRARY_PATH:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib"
export DYLD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/links3e442feaecb49/p/lib:/volume/conan_cache/reic_al/.conan2/p/procpc4b894f4e3426/p/lib:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/lib:$DYLD_LIBRARY_PATH"
export LN_MESSAGE_DEFINITION_DIRS="$LN_MESSAGE_DEFINITION_DIRS:/volume/conan_cache/reic_al/.conan2/p/links593b0d3fea288/p/message_definitions"