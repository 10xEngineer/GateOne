#!/usr/bin/env ruby

require 'yajl'
require 'highline/import'
require '10xlabs/microcloud'

puts "***"
puts "*** 10xEngineer.me lab connector"
puts "***"
puts

session_file = File.join(ENV["GO_USER_DIR"], ENV["GO_USER"], "session")

if File.exists?(session_file)
  session = Yajl::Parser.parse(IO.read(session_file))

  lab_token = session["lab"]
  config = "/etc/10xeng.yaml"
  
  unless File.exists?(config)
    puts "10xeng hostnode configuration file (#{config}) doesn't exist. GateOne server should run on a valid 10xeng-node instance"
    sleep 15
    exit
  end

  config = YAML::load(File.open(config))
  microcloud = TenxLabs::Microcloud.new(config["hostnode"]["endpoint"])

  begin
    lab = microcloud.get(:lab, lab_token)
  rescue Exception => e
    puts "Invalid lab: #{e.message}"

    sleep 15
  end

  puts "Lab environment"
  puts
  lab["vms"].each do |vm|
    puts "\t#{vm["vm_name"]} (#{vm["vm_type"]})\t#{vm["descriptor"]["ip_addr"]}\t#{vm["id"]}"
  end
  puts

  # TODO support vm_id passed using command line parameter
  vm_list = lab["vms"].map {|vm| vm["vm_name"]}

  target = ask("server? ") {|q| q.default = vm_list.first}

  unless vm_list.include?(target)
    puts "Invalid server!"
    sleep 10
    exit
  end

  cmd_parts = ["/opt/gateone/plugins/ssh/scripts/ssh_connect.py"]
  cmd_parts = cmd_parts + ARGV

  # TODO hardcoded user/port
  vm = lab["vms"].select {|vm| vm["vm_name"] == target}
  vm = vm.first

  cmd_parts << "ssh://ubuntu@#{vm["descriptor"]["ip_addr"]}"

  cmd = cmd_parts.join(" ")

  exec cmd

  sleep 60
else
  puts "WARNING: session file not found! Try to logout."

  ask("ready?") {|q| q.default = "y"}
end

