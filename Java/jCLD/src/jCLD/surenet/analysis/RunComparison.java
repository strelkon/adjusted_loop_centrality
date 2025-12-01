package jCLD.surenet.analysis;

import java.io.File;

/**
 * Test program to run the Java implementation on the OAIMicrosoft dataset
 * for cross-validation with the Python implementation.
 */
public class RunComparison {

    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("JAVA CLD ANALYSIS - CROSS-VALIDATION TEST");
        System.out.println("=".repeat(60));
        System.out.println();

        // Get the current directory
        String currentDir = System.getProperty("user.dir");
        System.out.println("Current directory: " + currentDir);

        // Set up paths
        String basePath = "";
        String filename = "OAIMicrosoft_edgelist.csv";

        // Check if file exists
        File testFile = new File(basePath + filename);
        if (!testFile.exists()) {
            System.err.println("ERROR: Input file not found: " + testFile.getAbsolutePath());
            System.err.println("Please run the conversion script first:");
            System.err.println("  cd python");
            System.err.println("  python convert_matrix_to_edgelist.py data/OAIMicrosoft_v6_17.11.25.xlsx ../Java/OAIMicrosoft_edgelist.csv");
            System.exit(1);
        }

        System.out.println("Input file: " + filename);
        System.out.println();

        try {
            // Create loader and load network
            LoopSetLoader loader = new LoopSetLoader();

            System.out.println("Loading network and detecting loops...");
            System.out.println("-".repeat(60));
            loader.loadLoopSet(basePath, filename);

            // Calculate scores
            System.out.println();
            System.out.println("Calculating centrality scores...");
            System.out.println("-".repeat(60));
            loader.getScores();

            // Write output files
            System.out.println();
            System.out.println("Writing output files...");
            System.out.println("-".repeat(60));

            String outputPrefix = "java_output_";
            loader.writeConceptNodeFile(basePath, outputPrefix + "concept_nodes.csv");
            loader.writeConceptLinkFile(basePath, outputPrefix + "concept_links.csv");
            loader.writeLoopNodeFile(basePath, outputPrefix + "loop_nodes.csv");
            loader.reportFileScoreSet(basePath, outputPrefix + "scores.txt");

            System.out.println();
            System.out.println("=".repeat(60));
            System.out.println("ANALYSIS COMPLETE");
            System.out.println("=".repeat(60));
            System.out.println();
            System.out.println("Output files created:");
            System.out.println("  - " + outputPrefix + "concept_nodes.csv");
            System.out.println("  - " + outputPrefix + "concept_links.csv");
            System.out.println("  - " + outputPrefix + "loop_nodes.csv");
            System.out.println("  - " + outputPrefix + "scores.txt");
            System.out.println();
            System.out.println("Compare these with the Python output files:");
            System.out.println("  - python/output_concept_nodes.csv");
            System.out.println("  - python/output_concept_links.csv");
            System.out.println("  - python/output_loop_nodes.csv");
            System.out.println("  - python/output_scores.txt");

        } catch (Exception e) {
            System.err.println();
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
