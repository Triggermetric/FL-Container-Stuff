const Reputation = artifacts.require("Reputation");

module.exports = function (deployer) {
  deployer.deploy(Reputation);
};
