/*
Read all input from webcrawl into map
BFS a certain number of levels from a given website to find recently visited
suggested sites created using most recently visited sites

random walk randomly traverses graph, and counts how many times a certain site is visited
*/

#include <iostream>
#include <vector>
#include <queue>
#include <map>
#include <climits>
#include <random>
#include <string>
#include <unistd.h>
#include <algorithm>

//Global Variables

typedef std::map<std::string, std::vector<std::string>>::iterator it;
int n = 5;
int s = 100;
std::string baddr;
std::string raddr;
bool b = false;
bool r = false;

//Graph class
class Graph{
	public:
		Graph();
		~Graph();
		void BFS();
		void randomWalk();
		void printSuggest(std::map<std::string, int>, char);
		int get_random(int);

	private:
		std::map<std::string,std::vector<std::string>> graph; //adjacency list
};

Graph::Graph(){
	//insert pairs into adjacency list
	std::string tmp1, tmp2;
	while(std::cin >> tmp1 >> std::ws >> tmp2){
		graph[tmp1].push_back(tmp2);\
		if(graph.find(tmp2) ==graph.end()){
			graph[tmp2].clear();
		}
	}
}

Graph::~Graph(){}

void Graph::BFS(){
	std::queue<it> q;
	it addr = graph.find(baddr);

	//check search is in adjacency list
	if(addr == graph.end()){
		return;
	}

	q.push(addr);
	int prev = 1;
	int next = 0;
	std::map<std::string, int> suggest;
	while(!q.empty()){
		it curr= q.front();
		q.pop();
		next = next+curr->second.size();

		if(suggest.find(curr->first) != suggest.end()){
			suggest[curr->first]++;
		}
		else{
			suggest[curr->first] = 1;
		}
		prev--;
		if(prev == 0){
			prev = next;
			next = 0;
			n--;
		}
		if(n < 0){
			printSuggest(suggest, 'b');
			break;
		}
		for(size_t i = 0; i < curr->second.size(); i++){
			std::string tmp = curr->second[i];
			it tmpIT = graph.find(tmp);
			q.push(tmpIT);
		}
	}
}

void Graph::randomWalk(){
	std::map<std::string, int> rand;
	it addr = graph.find(raddr);
	if (addr == graph.end()){
		return;
	}
	std::string previous = raddr;
	for(int i = 0; i < s; i++){
		size_t num = addr->second.size();
		std::string temp;
		if(num == 0){
			temp = previous;
		}
		else{
			temp = addr->second[get_random(num)];
		}
		it next = graph.find(temp);
		if(next != addr){
			auto search = rand.find(temp);
			if(search != rand.end()){
				rand[temp]++;
			}
			else{
				rand[temp] = 1;
			}
		}
		previous = addr->first;
		addr = next;
	}
	printSuggest(rand, 'r');
}

void Graph::printSuggest(std::map<std::string,int> s, char c){
	//print top 5 suggestions
	std::cout<<"Suggested Sites:"<<std::endl;
	std::vector<std::pair<std::string,int>> mapVec;
	for(auto i = s.begin(); i != s.end(); i++){
		if(c == 'b'){
			if(i->first == baddr){
				continue;
			}
		}
		else if(c == 'r'){
			if(i->first == raddr){
				continue;
			}
		}
		mapVec.push_back(std::make_pair(i->first,i->second));
	}
	std::sort(mapVec.begin(),mapVec.end(),[](const std::pair<std::string,int> &a, const std::pair<std::string,int> &b){ return a.second > b.second; });
	for(size_t i = 0; i < 5; i++){
		if(i >= mapVec.size()){
			break;
		}
		std::cout<<mapVec[i].first<<std::endl;
	}
}

int Graph::get_random(int size){
	std::random_device rd;
	std:: default_random_engine g(rd());
	std::uniform_int_distribution<int> d(0, size-1);
	return d(g);
}

//Non-class functions
void usage(int status){
	std::cout<<"usage: honeybee.cpp"<<std::endl;
	std::cout<<"	-b BADDR	BST for the address BADDR"<<std::endl;
	std::cout<<"	-r RADDR	Run random walk for the address RADDR"<<std::endl;
	std::cout<<"	-n N		number of levels to traverse for BST"<<std::endl;
	std::cout<<"	-s S		number of steps to take when random walking"<<std::endl;
	exit(status);
}

void parse(int argc, char *argv[]){
	int c;
	while ((c = getopt(argc, argv, "hb:r:n:s:")) != -1){
		switch (c){
			case 'b':
				b = true;
				baddr = optarg;
				break;
			case 'r':
				r = true;
				raddr = optarg;
				break;
			case 'n':
				n = std::atoi(optarg);
				break;
			case 's':
				s = std::atoi(optarg);
				break;
			case 'h':
				usage(0);
				break;
			default:
				usage(1);
				break;
		}
	}
}


int main(int argc, char *argv[]){
	parse(argc, argv); //parse command line
	Graph myGraph; //create graph
	//if b run a Breadth firts search
	if(b){
		myGraph.BFS();
	}
	//if r run a random walk search
	if(r){
		myGraph.randomWalk();
	}
	return 0;
}
