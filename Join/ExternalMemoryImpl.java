package Join;

import java.io.*;
import java.nio.file.Paths;
import java.util.Comparator;
import java.util.HashMap;
import java.util.PriorityQueue;

public class ExternalMemoryImpl extends IExternalMemory {

	private static final int MAX_ROWS_PER_BLOCK = 38;
	private static final int ROWS_IN_BUFFER = 247305; // 25 MiB buffer
	private int numSequences = 0;

	/**
	 * Writes contents of the memory buffer to a temporary file
	 * @param memoryBuffer - content to write to file
	 * @param out - file to write to
	 * @param numRows - number of rows to write to file
	 */
	private static void writeBlocksToFile(PriorityQueue<String> memoryBuffer, File out) throws
			IOException{
		FileWriter writer = new FileWriter(out, true);
		BufferedWriter buffWriter = new BufferedWriter(writer);
		while (memoryBuffer.size() > 0)
		{
			buffWriter.write(memoryBuffer.poll());
			buffWriter.newLine();
		}
		buffWriter.close();
		writer.close();
	}

	/**
	 * Splits the given input file denoted by its pathname into sorted smaller files representing blocks
	 * @param in - file to read from
	 * @param tmpPath - path for saving smaller files
	 * @param selection - substring that must be included in the first column
	 */
	private void sortBlocks(File in, String tmpPath, String selection) {
		LineComparator c = new LineComparator();
		PriorityQueue<String> blockContent = new PriorityQueue<>(ROWS_IN_BUFFER, c);
		int sequenceNum = 0;
		String blockFile;
		File cur;
		try {
			FileReader reader = new FileReader(in);
			BufferedReader buffer = new BufferedReader(reader);
			String curLine;
			while ((curLine = buffer.readLine()) != null) {
				if (blockContent.size() == ROWS_IN_BUFFER) {
					blockFile = in.getName() + String.valueOf(sequenceNum);
					cur = new File(tmpPath, blockFile);
					cur.deleteOnExit();
					writeBlocksToFile(blockContent, cur);
					blockContent.clear();
					++sequenceNum;
				}
				if (curLine.substring(0, 11).contains(selection)) {
					blockContent.add(curLine);
				}
			}
			buffer.close();
			reader.close();
			if (blockContent.size() > 0) {
				blockFile =in.getName() + String.valueOf(sequenceNum);
				cur = new File(tmpPath, blockFile);
				cur.deleteOnExit();
				writeBlocksToFile(blockContent, cur);
				++sequenceNum;
			}
			this.numSequences = sequenceNum;
		}
		catch (Exception e)
		{
			System.err.println("Sort error");
			e.printStackTrace();
		}
	}

	class LineComparator implements Comparator<String> {

		public int compare(String a, String b) {
			if (a == null || a.equals("")) {
				return 1;
			}
			if (b == null || b.equals("")) {
				return -1;
			}
			String[] line1Cols = a.split(" ");
			String[] line2Cols = b.split(" ");
			int comp = 0;
			for (int i = 0; i < line1Cols.length; i++) {
				comp = line1Cols[i].compareTo(line2Cols[i]);
				if (comp != 0) {
					return comp;
				}
			}
			return comp;
		}
	}


	/**
	 * Merges a file's sorted blocks
	 * @param name - the input file's name
	 * @param tmpPath - the path where the blocks are saved
	 * @param out - the output file
	 */
	private void mergeBlocks(String name, String tmpPath, File out) {
		int numSequences = this.numSequences;
		int argMinIdx;
		int finishedSequences = 0;
		HashMap<String, Integer> lineOrigin = new HashMap<>();
		LineComparator c = new LineComparator();
		PriorityQueue<String> buffer = new PriorityQueue<>(numSequences, c);
		String cur;
		PriorityQueue<String> block = new PriorityQueue<>(MAX_ROWS_PER_BLOCK, c);
		String minLine;
		FileReader[] readers = new FileReader[numSequences];
		BufferedReader[] buffReaders = new BufferedReader[numSequences];
		try {
			for (int i = 0; i < numSequences; i++) {
				readers[i] = new FileReader(new File(tmpPath, name + String.valueOf(i)));
				buffReaders[i] = new BufferedReader(readers[i]);
				cur = buffReaders[i].readLine();
				buffer.add(cur);
				lineOrigin.put(cur, i);
			}

			while (finishedSequences < numSequences) {
				minLine = buffer.poll();
				if (minLine == null || minLine.equals("")) {
					break;
				}
				block.add(minLine);
				if (block.size() == MAX_ROWS_PER_BLOCK) {
					writeBlocksToFile(block, out);
				}
				argMinIdx = lineOrigin.get(minLine);
				lineOrigin.remove(minLine, argMinIdx);
				cur = buffReaders[argMinIdx].readLine();
				lineOrigin.put(cur, argMinIdx);
				if (cur == null) {
					++finishedSequences;
					buffReaders[argMinIdx].close();
					readers[argMinIdx].close();
				}
				else {
					buffer.add(cur);
				}
			}
			if (block.size() > 0) {
				writeBlocksToFile(block, out);
			}
		}
		catch (Exception e) {
			System.err.println("Merge error");
			e.printStackTrace();
		}
	}

	@Override
	public void sort(String in, String out, String tmpPath) {
		File input = new File(in);
		File output = new File(out);
		sortBlocks(input, tmpPath, "");
		mergeBlocks(input.getName(), tmpPath, output);
	}


	@Override
	protected void join(String in1, String in2, String out, String tmpPath) {
		String Tr;
		String Ts;
		String TrCol;
		String TsCol;
		int comp;
		File output = new File(out);
		try {
			FileReader reader1 = new FileReader(in1);
			FileReader reader2 = new FileReader(in2);
			FileWriter writer = new FileWriter(output, true);
			BufferedWriter buffer = new BufferedWriter(writer);
			BufferedReader buffReader1 = new BufferedReader(reader1);
			BufferedReader buffReader2 = new BufferedReader(reader2);
			Tr = buffReader1.readLine();
			Ts = buffReader2.readLine();
			while (Tr != null && Ts != null) {
				TrCol = Tr.substring(0, 11);
				TsCol = Ts.substring(0, 11);
				comp = TrCol.compareTo(TsCol);
				if (comp < 0) {
					Tr = buffReader1.readLine();
					continue;
				}
				else if (comp > 0) {
					Ts = buffReader1.readLine();
					continue;
				}
				while (Ts != null && comp == 0) {
					buffer.write(Tr + Ts.substring(TsCol.length() - 1));
					buffer.newLine();
					Ts = buffReader2.readLine();
					if (Ts != null) {
						TsCol = Ts.substring(0, 11);
						comp = TrCol.compareTo(TsCol);
					}
				}
			}
			buffReader1.close();
			buffReader2.close();
			reader1.close();
			reader2.close();
			buffer.close();
			writer.close();
		}
		catch (Exception e) {
			System.err.println("Join error");
			e.printStackTrace();
		}
	}

	@Override
	protected void select(String in, String out, String substrSelect, String tmpPath) {
		String curLine;
		try {
			FileReader reader = new FileReader(in);
			BufferedReader buffReader = new BufferedReader(reader);
			FileWriter writer = new FileWriter(out);
			BufferedWriter bufferedWriter = new BufferedWriter(writer);
			while ((curLine = buffReader.readLine()) != null) {
				if (curLine.substring(0, 11).contains(substrSelect)) {
					bufferedWriter.write(curLine);
					bufferedWriter.newLine();
				}
			}
			buffReader.close();
			reader.close();
			bufferedWriter.close();
			writer.close();
		}
		catch (Exception e) {
			e.printStackTrace();
		}
		
	}

	@Override
	public void joinAndSelectEfficiently(String in1, String in2, String out,
			String substrSelect, String tmpPath) {

		String outFileName = new File(out).getName();
		String tmpFileName1 = outFileName.substring(0, outFileName.lastIndexOf('.'))
				+ "_intermed1" + outFileName.substring(outFileName.lastIndexOf('.'));
		String tmpOut1 = Paths.get(tmpPath, tmpFileName1).toString();
		String tmpFileName2 = outFileName.substring(0, outFileName.lastIndexOf('.'))
				+ "_intermed2" + outFileName.substring(outFileName.lastIndexOf('.'));
		String tmpOut2 = Paths.get(tmpPath, tmpFileName2).toString();
		File input1 = new File(in1);
		File input2 = new File(in2);
		File out1 = new File(tmpOut1);
		File out2 = new File(tmpOut2);
		out1.deleteOnExit();
		out2.deleteOnExit();
		sortBlocks(input1, tmpPath, substrSelect);
		mergeBlocks(input1.getName(), tmpPath, out1);
		sortBlocks(input2, tmpPath, substrSelect);
		mergeBlocks(input2.getName(), tmpPath, out2);
		join(tmpOut1, tmpOut2, out, tmpPath);
		
	}


}